from __future__ import annotations

from dataclasses import dataclass
import sys
import time


@dataclass
class Progress:
    """Small stderr progress reporter used by archive operations."""

    total: int = 0
    done: int = 0
    label: str = ""
    enabled: bool = True

    def __post_init__(self):
        self.started = time.monotonic()

    def update(self, amount: int = 1, label: str | None = None) -> None:
        self.done += amount
        if label is not None:
            self.label = label
        if not self.enabled:
            return
        elapsed = max(time.monotonic() - self.started, 1e-6)
        rate = self.done / elapsed
        if self.total:
            pct = min(100.0, self.done * 100.0 / self.total)
            msg = f"\r{self.label + ': ' if self.label else ''}{pct:6.2f}% {self.done}/{self.total}"
        else:
            msg = f"\r{self.label + ': ' if self.label else ''}{self.done} items"
        msg += f"  {rate:,.1f}/s"
        print(msg, end="", file=sys.stderr, flush=True)

    def complete(self, label: str | None = None) -> None:
        if label is not None:
            self.label = label
        if self.enabled:
            elapsed = max(time.monotonic() - self.started, 1e-6)
            rate = self.done / elapsed if self.done else 0.0
            msg = f"\r{self.label + ': ' if self.label else ''}100.00% {self.done}/{self.total}  {rate:,.1f}/s"
            print(msg, file=sys.stderr)

    def finish(self) -> None:
        self.complete()
