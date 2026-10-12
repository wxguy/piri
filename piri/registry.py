from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import Iterable

from .backend import ArchiveBackend, BackendCapability, BackendRegistration
from .errors import BackendError

ENTRY_POINT_GROUP = "piri.backends"


class BackendRegistry:
    """Discover, register and resolve piri archive backends.

    Built-in backends are registered first. Optional Python packages may
    expose an ``piri.backends`` entry point returning either an
    ``ArchiveBackend`` instance or a zero-argument callable returning one.
    Plugin failures are isolated and reported through ``load_errors`` so an
    unrelated optional backend cannot make the core CLI unusable.
    """

    def __init__(self) -> None:
        self._registrations: dict[str, BackendRegistration] = {}
        self.load_errors: dict[str, str] = {}

    def register(self, backend: ArchiveBackend, *, source: str = "builtin",
                 priority: int = 100, formats: Iterable[str] | None = None) -> None:
        name = str(getattr(backend, "name", "")).strip()
        if not name:
            raise ValueError("backend must define a non-empty name")
        supported = tuple(formats or getattr(backend, "formats", ()))
        if not supported:
            raise ValueError(f"backend {name!r} does not declare any formats")
        self._registrations[name] = BackendRegistration(
            name=name, backend=backend, source=source,
            priority=priority, formats=tuple(dict.fromkeys(supported)),
        )

    def registrations(self) -> tuple[BackendRegistration, ...]:
        return tuple(sorted(self._registrations.values(), key=lambda r: (-r.priority, r.name)))

    def get(self, name: str) -> ArchiveBackend:
        try:
            return self._registrations[name].backend
        except KeyError as exc:
            raise BackendError(f"unknown archive backend: {name}") from exc

    def registration_for_format(self, fmt: str) -> BackendRegistration | None:
        candidates = [r for r in self.registrations() if r.supports(fmt)]
        if not candidates:
            return None
        # Prefer an available backend. If multiple are available, registration
        # priority decides; this lets a site plugin override a built-in backend.
        available: list[BackendRegistration] = []
        for r in candidates:
            try:
                if r.backend.capability(fmt).available:
                    available.append(r)
            except Exception:
                continue
        return (available or candidates)[0]

    def capability_rows(self) -> list[dict]:
        rows: list[dict] = []
        for registration in self.registrations():
            for fmt in registration.formats:
                try:
                    cap = registration.backend.capability(fmt)
                    row = {
                        "backend": registration.name,
                        "source": registration.source,
                        "format": fmt,
                        "available": cap.available,
                        "read": cap.read,
                        "write": cap.write,
                        "test": cap.test,
                        "parallel_compression": cap.parallel_compression,
                        "parallel_extraction": cap.parallel_extraction,
                        "streaming": cap.streaming,
                        "safe_preflight": cap.safe_preflight,
                        "executable": cap.executable,
                        "version": cap.version,
                        "reason": cap.reason,
                    }
                except Exception as exc:
                    row = {
                        "backend": registration.name,
                        "source": registration.source,
                        "format": fmt,
                        "available": False,
                        "read": False,
                        "write": False,
                        "test": False,
                        "parallel_compression": False,
                        "parallel_extraction": False,
                        "streaming": False,
                        "safe_preflight": False,
                        "executable": None,
                        "version": None,
                        "reason": str(exc),
                    }
                rows.append(row)
        return rows

    def discover_entry_points(self) -> None:
        try:
            eps = metadata.entry_points()
            selected = eps.select(group=ENTRY_POINT_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_POINT_GROUP, ())
        except Exception as exc:
            self.load_errors["<entry-points>"] = str(exc)
            return
        for ep in selected:
            try:
                loaded = ep.load()
                backend = loaded() if callable(loaded) and not hasattr(loaded, "capability") else loaded
                self.register(backend, source=f"plugin:{ep.name}", priority=200)
            except Exception as exc:
                self.load_errors[ep.name] = str(exc)


def default_registry() -> BackendRegistry:
    from .native_backend import NativeBackend

    registry = BackendRegistry()
    registry.register(NativeBackend(), source="builtin", priority=100)
    from .libarchive_backend import LibarchiveBackend
    registry.register(LibarchiveBackend(), source="builtin-optional", priority=80)
    from .image_backend import ImageBackend
    registry.register(ImageBackend(), source="builtin-optional", priority=90)
    registry.discover_entry_points()
    return registry
