"""Métricas de latência e monitoring."""

from typing import Dict, List
from collections import defaultdict
import statistics


class MetricsCollector:
    """Coletor de métricas."""

    def __init__(self):
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)

    def record_latency(self, endpoint: str, latency_ms: float) -> None:
        """Grava latência."""
        self._latencies[endpoint].append(latency_ms)

    def get_percentile(self, endpoint: str, percentile: float) -> float:
        """Retorna percentil de latência."""
        latencies = self._latencies.get(endpoint, [])
        if not latencies:
            return 0.0

        sorted_latencies = sorted(latencies)
        index = int(len(sorted_latencies) * percentile)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def increment_counter(self, name: str) -> None:
        """Incrementa contador."""
        self._counters[name] += 1

    def get_counter(self, name: str) -> int:
        """Retorna valor do contador."""
        return self._counters.get(name, 0)

    def get_all_metrics(self) -> Dict:
        """Retorna todas métricas."""
        result = {"latencies": {}, "counters": dict(self._counters)}

        for endpoint, latencies in self._latencies.items():
            result["latencies"][endpoint] = {
                "p50": self.get_percentile(endpoint, 0.50),
                "p95": self.get_percentile(endpoint, 0.95),
                "p99": self.get_percentile(endpoint, 0.99),
                "count": len(latencies),
            }

        return result

    def reset(self) -> None:
        """Reseta métricas."""
        self._latencies.clear()
        self._counters.clear()


# Global collector
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Retorna coletor global."""
    return _metrics
