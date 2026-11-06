"""Download an EgoObjects slice capped by bytes, from the front of the zip.

The full image zip is about 37 GiB. Each local file header stores that file's
size, so a prefix of the zip still decompresses. Official test images are read
(they count toward the cap) and not written.

Default cap is 9 GB of zip bytes. Annotation JSON is about 0.24 GB on top,
which keeps the total under 10 GB.
"""

from __future__ import annotations

import argparse
import json
import struct
import time
import urllib.request
import zlib
from pathlib import Path

from ego_index import FILES, ZIP_NAME, ZIP_SIZE, file_url

LOCAL = b"PK\x03\x04"
HEADER = struct.Struct("<HHHHHIIIHH")


def _request(url: str, range_header: str | None = None):
    headers = {"User-Agent": "josh-vision-training"}
    if range_header:
        headers["Range"] = range_header
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=300)


def _categories_readable(path: Path) -> bool:
    """A pretty-printed local copy is still the category list. Keep it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    categories = data.get("categories") if isinstance(data, dict) else None
    return isinstance(categories, list) and len(categories) > 0


def ensure_file(raw_dir: Path, name: str, size: int) -> None:
    path = raw_dir / name
    if path.is_file() and path.stat().st_size == size:
        print(f"have {name} ({size} bytes)")
        return
    if name == "Meta_EgoObjects_Val.json" and path.is_file() and _categories_readable(path):
        print(f"have {name} ({path.stat().st_size} bytes)")
        return
    print(f"download {name}")
    tmp = path.with_suffix(path.suffix + ".part")
    got = 0
    with _request(file_url(name)) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            handle.write(chunk)
            got += len(chunk)
    if got != size:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"{name} is {got} bytes, expected {size}. The mirror changed.")
    tmp.replace(path)


def ensure_annotations(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name, size in FILES.values():
        ensure_file(raw_dir, name, size)


def keep_urls(raw_dir: Path) -> set[str]:
    """Train and val file names. Anything marked test is left out."""
    keep: set[str] = set()
    blocked: set[str] = set()
    for key in ("train_split", "val_and_test"):
        with (raw_dir / FILES[key][0]).open(encoding="utf-8") as handle:
            data = json.load(handle)
        for image in data["images"]:
            subset = image.get("subset") or "train"
            url = image["url"]
            if subset == "test":
                blocked.add(url)
                keep.discard(url)
            elif url not in blocked:
                keep.add(url)
        del data
    return keep


class ZipStream:
    """Read forward through an HTTP range. A dropped connection reopens at `abs`."""

    def __init__(self, url: str, start: int) -> None:
        self.url = url
        self.abs = start
        self.fetched = 0
        self._resp = None
        self._buf = b""
        self._empty_reads = 0

    def close(self) -> None:
        if self._resp is not None:
            self._resp.close()
            self._resp = None

    def _open(self) -> None:
        self.close()
        response = _request(self.url, f"bytes={self.abs}-")
        if getattr(response, "status", 206) not in (200, 206):
            response.close()
            raise SystemExit("zip range request was refused")
        total = response.headers.get("Content-Range", "")
        if str(ZIP_SIZE) not in total:
            response.close()
            raise SystemExit(f"zip size changed on the mirror ({total or 'no Content-Range'})")
        self._resp = response
        self._empty_reads = 0

    def read(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            if not self._buf:
                if self._resp is None:
                    self._open()
                try:
                    chunk = self._resp.read(1 << 20)
                except Exception as exc:
                    print(f"read failed at byte {self.abs}: {exc}")
                    self._resp = None
                    time.sleep(2)
                    continue
                if not chunk:
                    self._empty_reads += 1
                    self._resp = None
                    if self._empty_reads > 4:
                        raise SystemExit(f"zip ended early at byte {self.abs}")
                    time.sleep(1)
                    continue
                self._empty_reads = 0
                self._buf = chunk
            take = min(n - len(out), len(self._buf))
            out += self._buf[:take]
            self._buf = self._buf[take:]
            self.abs += take
            self.fetched += take
        return bytes(out)


def _state_path(raw_dir: Path) -> Path:
    return raw_dir / "download_state.json"


def load_state(raw_dir: Path) -> dict:
    path = _state_path(raw_dir)
    if not path.is_file():
        return {"zip_offset": 0, "fetched": 0, "written": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def download_zip(raw_dir: Path, max_bytes: int, restart: bool) -> None:
    images_dir = raw_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    state = {"zip_offset": 0, "fetched": 0, "written": 0} if restart else load_state(raw_dir)
    already = int(state["fetched"])
    if already >= max_bytes:
        print(f"already fetched {already} bytes (cap {max_bytes})")
        return

    keep = keep_urls(raw_dir)
    print(f"train and val filenames: {len(keep)}")
    stream = ZipStream(file_url(ZIP_NAME), int(state["zip_offset"]))
    written = int(state["written"])
    skipped = 0
    checkpoint = {"zip_offset": int(state["zip_offset"]), "fetched": already, "written": written}

    def running() -> int:
        return already + stream.fetched

    try:
        while running() < max_bytes:
            file_start = stream.abs
            fetched_at_file = stream.fetched
            header = stream.read(30)
            if header[:4] != LOCAL:
                checkpoint = {"zip_offset": stream.abs, "fetched": running(), "written": written}
                print(f"stopped: no local file header at byte {file_start}")
                break
            _ver, flag, method, _tm, _dt, _crc, comp_size, _uncomp, name_len, extra_len = HEADER.unpack_from(
                header, 4
            )
            name = stream.read(name_len + extra_len)[:name_len].decode("utf-8", "replace")
            if flag & 0x1:
                raise SystemExit("zip member is encrypted")
            if flag & 0x8 or method not in (0, 8):
                raise SystemExit(f"unexpected zip member {name!r} method={method} flag={flag}")

            base = name.replace("\\", "/").split("/")[-1]
            want = base in keep and base.lower().endswith((".jpg", ".jpeg"))
            if running() + comp_size > max_bytes:
                checkpoint = {
                    "zip_offset": file_start,
                    "fetched": already + fetched_at_file,
                    "written": written,
                }
                print("cap reached; next image would pass it")
                break

            if not want or comp_size == 0:
                stream.read(comp_size)
                if base and base not in keep:
                    skipped += 1
                continue

            blob = stream.read(comp_size)
            raw = blob if method == 0 else zlib.decompress(blob, -15)
            if not raw.startswith(b"\xff\xd8"):
                print(f"skip {base}: not a JPEG after decompress")
                continue
            (images_dir / base).write_bytes(raw)
            written += 1
            checkpoint = {"zip_offset": stream.abs, "fetched": running(), "written": written}
            if written % 25 == 0:
                print(f"wrote {written}, fetched {running() / 1024**3:.2f} GiB, last {base}")
                _state_path(raw_dir).write_text(json.dumps(checkpoint), encoding="utf-8")
    finally:
        _state_path(raw_dir).write_text(json.dumps(checkpoint), encoding="utf-8")
        stream.close()

    print(
        f"wrote {written} images, passed {skipped} other files, "
        f"fetched {checkpoint['fetched'] / 1024**3:.2f} GiB"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download an EgoObjects slice under a byte cap.")
    parser.add_argument(
        "--max-gb",
        type=float,
        default=9.0,
        help="Zip bytes to read. Default 9. JSON adds about 0.24 GB.",
    )
    parser.add_argument("--restart", action="store_true", help="Read the zip from byte 0 again.")
    parser.add_argument("--raw", type=Path, default=Path(__file__).resolve().parent / "raw")
    args = parser.parse_args()
    if args.max_gb <= 0:
        raise SystemExit("--max-gb must be positive")
    ensure_annotations(args.raw)
    download_zip(args.raw, int(args.max_gb * (1024**3)), args.restart)


if __name__ == "__main__":
    main()
