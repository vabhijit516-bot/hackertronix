"""Performance profiling helpers for the vision pipeline."""

from __future__ import annotations

import time
from typing import Any, Dict, List


class PerformanceProfiler:
    """Measure simple latency and FPS metrics."""

    def __init__(self) -> None:
        self.samples: List[float] = []

    def measure(self, operation: str, fn, *args, **kwargs) -> Any:
        """Measure the runtime of an operation."""
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.samples.append(elapsed_ms)
        return result

    def metrics(self) -> Dict[str, Any]:
        """Return average and maximum latency metrics."""
        if not self.samples:
            return {"fps": 0.0, "average_latency_ms": 0.0, "max_latency_ms": 0.0}
        average = sum(self.samples) / len(self.samples)
        return {"fps": round(1000.0 / max(average, 1e-6), 2), "average_latency_ms": round(average, 2), "max_latency_ms": round(max(self.samples), 2)}
