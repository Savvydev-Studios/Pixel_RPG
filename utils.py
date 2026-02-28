from __future__ import annotations
from dataclasses import dataclass
import time


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


@dataclass
class DeltaTime:
    _last: float = time.perf_counter()

    def tick(self) -> float:
        now = time.perf_counter()
        dt = now - self._last
        self._last = now
        return dt