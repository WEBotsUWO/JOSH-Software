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

    def allow(self, now: float) -> bool:
        """Return True when this timestamp may be emitted."""
        raise NotImplementedError("Rate: gate emits at self.hz and count skips.")


if __name__ == "__main__":
    raise SystemExit("Rate: feed a burst of timestamps and print allows versus skipped.")
