"""Utilities for collecting server metrics."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List

import psutil


@dataclass
class MetricSnapshot:
    """Represents a point-in-time view of key system metrics."""

    timestamp: float
    cpu_percent: float
    per_core_cpu: List[float]
    load_average: List[float]
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    swap_percent: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mbps: float
    network_recv_mbps: float
    boot_time: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


class MetricsCollector:
    """Collects metrics and calculates deltas where required."""

    def __init__(self) -> None:
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()

    def collect(self) -> Dict[str, float]:
        now = time.time()
        cpu_percent = psutil.cpu_percent(interval=None)
        per_core_cpu = psutil.cpu_percent(interval=None, percpu=True)

        try:
            load_avg = list(os.getloadavg())
        except (AttributeError, OSError):  # pragma: no cover - platform specific
            load_avg = [0.0, 0.0, 0.0]

        virtual_mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")

        current_net = psutil.net_io_counters()
        elapsed = max(now - self._last_time, 1e-6)
        sent_bytes = current_net.bytes_sent - self._last_net.bytes_sent
        recv_bytes = current_net.bytes_recv - self._last_net.bytes_recv
        sent_mbps = (sent_bytes * 8 / 1_000_000) / elapsed
        recv_mbps = (recv_bytes * 8 / 1_000_000) / elapsed

        snapshot = MetricSnapshot(
            timestamp=now,
            cpu_percent=cpu_percent,
            per_core_cpu=per_core_cpu,
            load_average=load_avg,
            memory_percent=virtual_mem.percent,
            memory_used_gb=round(virtual_mem.used / (1024 ** 3), 2),
            memory_total_gb=round(virtual_mem.total / (1024 ** 3), 2),
            swap_percent=swap.percent,
            disk_percent=disk.percent,
            disk_used_gb=round(disk.used / (1024 ** 3), 2),
            disk_total_gb=round(disk.total / (1024 ** 3), 2),
            network_sent_mbps=round(sent_mbps, 3),
            network_recv_mbps=round(recv_mbps, 3),
            boot_time=psutil.boot_time(),
        )

        self._last_net = current_net
        self._last_time = now
        return snapshot.to_dict()


collector = MetricsCollector()
