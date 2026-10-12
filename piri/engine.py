from __future__ import annotations

from pathlib import Path
import os
import shutil
import tempfile
import time

from .backends import create_archive, extract_archive, list_archive, backend_info, test_archive
from .detect import detect_format
from .errors import FormatError
from .formats import from_extension, get_format
from .policy import ExtractionPolicy, check_destination
from .metadata import MetadataPolicy
from .progress import Progress
from .results import OperationResult
from .telemetry import source_file_stats, PeakRSSMonitor, cpu_times
from .registry import default_registry


class ArchiveEngine:
    """Stable Python API for archive creation, listing, testing and extraction."""

    def __init__(self, registry=None):
        self.registry = registry or default_registry()

    def backend_capabilities(self) -> list[dict]:
        return self.registry.capability_rows()

    def create(self, source: str | Path, destination: str | Path,
               jobs: int = 1, metadata: MetadataPolicy | None = None,
               progress: Progress | None = None) -> str | OperationResult:
        source, destination = Path(source), Path(destination)
        if not source.is_dir():
            raise ValueError(f"source directory does not exist: {source}")
        if jobs < 1:
            raise ValueError("jobs must be >= 1")
        spec = from_extension(str(destination))
        if not spec or not spec.write:
            raise FormatError(f"no writable archive format for {destination}")
        registration = self.registry.registration_for_format(spec.name)
        if registration is None:
            raise FormatError(f"no backend registered for format: {spec.name}")
        capability = registration.backend.capability(spec.name)
        if not capability.available or not capability.write:
            raise FormatError(f"archive backend unavailable: {spec.name} ({registration.name})")
        cpu0 = cpu_times()
        t0 = time.perf_counter()
        with PeakRSSMonitor() as monitor:
            registration.backend.create(source, destination, spec.name, jobs, progress=progress, metadata=metadata)
        elapsed = time.perf_counter() - t0
        cpu1 = cpu_times()
        file_count, source_bytes = source_file_stats(source)
        output_bytes = destination.stat().st_size if destination.exists() else 0
        return OperationResult("compress", spec.name, backend_info(spec.name).compressor, elapsed,
                               bytes_processed=source_bytes, members_processed=file_count,
                               source_bytes=source_bytes, output_bytes=output_bytes,
                               peak_rss_kib=monitor.peak_kib,
                               cpu_user_seconds=max(0.0, cpu1[0] - cpu0[0]),
                               cpu_system_seconds=max(0.0, cpu1[1] - cpu0[1]))

    def detect(self, archive: str | Path):
        return detect_format(archive)

    def test(self, archive: str | Path) -> OperationResult:
        """Test archive integrity without extracting it."""
        archive = Path(archive)
        if not archive.is_file():
            raise ValueError(f"archive does not exist: {archive}")
        detected = detect_format(archive)
        spec = get_format(detected.name)
        if not spec or "test" not in spec.operations:
            raise FormatError(f"integrity testing is not supported for: {detected.name}")
        registration = self.registry.registration_for_format(detected.name)
        if registration is None:
            raise FormatError(f"no backend registered for format: {detected.name}")
        cpu0 = cpu_times()
        t0 = time.perf_counter()
        with PeakRSSMonitor() as monitor:
            members = registration.backend.test(archive, detected.name)
        elapsed = time.perf_counter() - t0
        cpu1 = cpu_times()
        archive_bytes = archive.stat().st_size
        return OperationResult("test", detected.name, backend_info(detected.name).compressor, elapsed,
                               bytes_processed=archive_bytes, members_processed=members,
                               source_bytes=archive_bytes,
                               peak_rss_kib=monitor.peak_kib,
                               cpu_user_seconds=max(0.0, cpu1[0] - cpu0[0]),
                               cpu_system_seconds=max(0.0, cpu1[1] - cpu0[1]))

    def list(self, archive: str | Path) -> list[str]:
        detected = detect_format(archive)
        spec = get_format(detected.name)
        if not spec or "list" not in spec.operations:
            raise FormatError(f"listing is not supported for: {detected.name}")
        registration = self.registry.registration_for_format(detected.name)
        if registration is None:
            raise FormatError(f"no backend registered for format: {detected.name}")
        return registration.backend.list(Path(archive), detected.name)

    @staticmethod
    def _merge_staged(stage: Path, destination: Path, policy: ExtractionPolicy) -> None:
        """Merge a validated staging tree while applying overwrite=skip."""
        for src in sorted(stage.rglob("*"), key=lambda p: (len(p.relative_to(stage).parts), p.name)):
            rel = src.relative_to(stage)
            dst = destination / rel
            if src.is_dir() and not src.is_symlink():
                dst.mkdir(parents=True, exist_ok=True)
                continue
            if dst.exists() or dst.is_symlink():
                if policy.overwrite == "skip":
                    continue
                if policy.overwrite == "replace":
                    if dst.is_dir() and not dst.is_symlink():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_symlink():
                dst.symlink_to(os.readlink(src), target_is_directory=src.is_dir())
            else:
                shutil.copy2(src, dst, follow_symlinks=False)

    def extract(self, archive: str | Path, destination: str | Path,
                policy: ExtractionPolicy | None = None,
                metadata: MetadataPolicy | None = None,
                progress: Progress | None = None,
                jobs: int = 1, atomic: bool = False) -> str | OperationResult:
        archive, destination = Path(archive), Path(destination)
        policy = policy or ExtractionPolicy()
        if jobs < 1:
            raise ValueError("jobs must be >= 1")
        if atomic:
            if destination.exists():
                raise FileExistsError(f"--atomic requires a non-existent destination: {destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
        else:
            check_destination(destination, policy)
        detected = detect_format(archive)
        spec = get_format(detected.name)
        if not spec or "extract" not in spec.operations:
            raise FormatError(f"extraction is not supported for: {detected.name}")
        registration = self.registry.registration_for_format(detected.name)
        if registration is None:
            raise FormatError(f"no backend registered for format: {detected.name}")

        cpu0 = cpu_times()
        t0 = time.perf_counter()
        # Strict overwrite policy is checked before any extraction.
        if policy.overwrite == "error":
            root = destination.resolve()
            for name in registration.backend.list(archive, detected.name):
                target = (root / Path(*name.replace("\\", "/").split("/"))).resolve()
                if target != root and target.exists():
                    raise FileExistsError(f"destination already contains: {target}")

        stage_context = (tempfile.TemporaryDirectory(prefix=f".{destination.name}.piri-", dir=str(destination.parent)) if atomic else None)
        try:
            target = Path(stage_context.name) if stage_context else destination
            with PeakRSSMonitor() as monitor:
                if policy.overwrite == "skip":
                    with tempfile.TemporaryDirectory(prefix="piri-stage-") as td:
                        stage = Path(td)
                        registration.backend.extract(archive, stage, detected.name, policy=policy, progress=progress, metadata=metadata, jobs=jobs)
                        destination.mkdir(parents=True, exist_ok=True)
                        self._merge_staged(stage, destination, policy)
                else:
                    registration.backend.extract(archive, target, detected.name, policy=policy, progress=progress, metadata=metadata, jobs=jobs)
                    if atomic:
                        target.rename(destination)
            elapsed = time.perf_counter() - t0
        finally:
            if stage_context:
                stage_context.cleanup()
        cpu1 = cpu_times()
        archive_bytes = archive.stat().st_size
        return OperationResult("extract", detected.name, backend_info(detected.name).compressor, elapsed,
                               bytes_processed=archive_bytes, members_processed=progress.done if progress else 0,
                               source_bytes=archive_bytes, peak_rss_kib=monitor.peak_kib,
                               cpu_user_seconds=max(0.0, cpu1[0] - cpu0[0]),
                               cpu_system_seconds=max(0.0, cpu1[1] - cpu0[1]))
