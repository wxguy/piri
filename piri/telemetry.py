from __future__ import annotations

import os
import time
import threading
from dataclasses import dataclass


@dataclass
class Timer:
    started: float = 0.0

    def __enter__(self):
        self.started = time.perf_counter()
        return self

    def __exit__(self, *_exc):
        return False

    @property
    def elapsed(self) -> float:
        return max(0.0, time.perf_counter() - self.started)


def _rss_kib(pid: int) -> int | None:
    try:
        with open(f"/proc/{pid}/status", encoding="ascii") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def _descendants(pid: int) -> set[int]:
    result: set[int] = set()
    queue = [pid]
    while queue:
        parent = queue.pop()
        try:
            children = Path(f"/proc/{parent}/task/{parent}/children").read_text().split()
        except OSError:
            continue
        for item in children:
            try:
                child = int(item)
            except ValueError:
                continue
            if child not in result:
                result.add(child)
                queue.append(child)
    return result


# Local import avoids making pathlib part of the public telemetry surface.
from pathlib import Path


class PeakRSSMonitor:
    """Best-effort peak RSS sampler for this process and its child processes."""

    def __init__(self, interval: float = 0.05):
        self.interval = max(0.01, interval)
        self.peak_kib: int | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _sample(self):
        pids = {os.getpid(), *_descendants(os.getpid())}
        values = [_rss_kib(pid) for pid in pids]
        values = [v for v in values if v is not None]
        if values:
            # RSS values of independent processes are additive for this
            # process tree, which is a more useful operational figure than
            # reporting only the Python parent's RSS.
            value = sum(values)
            self.peak_kib = max(self.peak_kib or 0, value)

    def _run(self):
        while not self._stop.is_set():
            self._sample()
            self._stop.wait(self.interval)
        self._sample()

    def __enter__(self):
        self._sample()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *_exc):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self._sample()
        return False


def current_rss_kib() -> int | None:
    return _rss_kib(os.getpid())


def cpu_times() -> tuple[float, float]:
    """Return process CPU user/system seconds, including terminated children."""
    try:
        import resource
        own = resource.getrusage(resource.RUSAGE_SELF)
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        return (own.ru_utime + children.ru_utime,
                own.ru_stime + children.ru_stime)
    except (ImportError, AttributeError):
        return (0.0, 0.0)


def source_file_stats(root):
    """Return (file_count, byte_count) without loading file contents."""
    count = 0
    total = 0
    for path in root.rglob("*"):
        try:
            if path.is_file():
                count += 1
                total += path.stat().st_size
        except OSError:
            continue
    return count, total
