"""Metrics collection utilities (placeholder)."""

from typing import Any


class MetricsCollector:
    """Collector for application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: dict[str, Any] = {}

    def increment(self, metric_name: str, value: int = 1):
        """
        Increment a counter metric.

        Args:
            metric_name: Name of the metric
            value: Amount to increment by
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += value

    def gauge(self, metric_name: str, value: float):
        """
        Set a gauge metric.

        Args:
            metric_name: Name of the metric
            value: Value to set
        """
        self.metrics[metric_name] = value

    def get_metrics(self) -> dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()


# Global metrics collector
metrics = MetricsCollector()
