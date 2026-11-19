"""Rate role for Vision Training step 1.

EmitGate.allow(now) returns True at most `hz` times per second.
`now` is time.perf_counter() seconds, passed in so a test can avoid sleeping.
The first call returns True. Later calls return True only when
now - last_emit >= 1/hz. Each False increments `skipped`.
"""


class EmitGate:
    def __init__(self, hz: float = 10.0) -> None:
        if hz <= 0:
            raise ValueError("hz must be positive")
        self.hz = hz
        self.skipped = 0
        self._period = 1.0 / hz
        self._last_emit: float | None = None

    def allow(self, now: float) -> bool:
        """Return True when this timestamp may be emitted."""
        if self._last_emit is None or now - self._last_emit >= self._period:
            self._last_emit = now
            return True
        self.skipped += 1
        return False


if __name__ == "__main__":
    # Simulated 1000 Hz camera for 3 seconds: timestamps 0.000, 0.001, ..., 2.999.
    camera_hz = 1000
    seconds = 3
    stamps = [i / camera_hz for i in range(camera_hz * seconds)]

    gate = EmitGate()  # default 10 Hz
    allowed_at = [t for t in stamps if gate.allow(t)]
    allows = len(allowed_at)

    gaps_ok = all(b - a >= 1.0 / gate.hz for a, b in zip(allowed_at, allowed_at[1:]))
    # Check every 1 s window starting at an emit holds at most hz emits.
    per_second_ok = all(
        sum(1 for t in allowed_at if start <= t < start + 1.0) <= gate.hz
        for start in allowed_at
    )
    total_ok = allows + gate.skipped == len(stamps)
    count_ok = abs(allows - gate.hz * seconds) <= 1  # "about 10 per second"

    print(f"timestamps fed: {len(stamps)} over {seconds} s at {camera_hz} Hz")
    print(f"allowed: {allows} (~{allows / seconds:.1f}/s)")
    print(f"skipped: {gate.skipped}")

    ok = gaps_ok and per_second_ok and total_ok and count_ok
    print("PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)
