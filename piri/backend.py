from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class BackendCapability:
    """Capabilities exposed by a backend for one archive format."""

    name: str
    format: str
    available: bool
    read: bool
    write: bool
    test: bool = True
    parallel_compression: bool = False
    parallel_extraction: bool = False
    streaming: bool = False
    safe_preflight: bool = False
    executable: str | None = None
    version: str | None = None
    reason: str | None = None


class ArchiveBackend(Protocol):
    """Stable backend contract used by piri and third-party plugins.

    A backend may support one or many formats. Methods should raise
    ``BackendError`` (or a more specific piri error) rather than returning
    ad-hoc status values.
    """

    name: str
    formats: Sequence[str]

    def capability(self, fmt: str) -> BackendCapability: ...
    def create(self, source: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs: Any) -> None: ...
    def extract(self, archive: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs: Any) -> None: ...
    def list(self, archive: Path, fmt: str, **kwargs: Any) -> list[str]: ...
    def test(self, archive: Path, fmt: str, **kwargs: Any) -> int: ...


@dataclass(frozen=True)
class BackendRegistration:
    """Metadata about a registered backend implementation."""

    name: str
    backend: ArchiveBackend
    source: str = "builtin"
    priority: int = 100
    formats: tuple[str, ...] = field(default_factory=tuple)

    def supports(self, fmt: str) -> bool:
        return fmt in self.formats
