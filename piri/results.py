from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OperationResult:
    operation: str
    format: str
    backend: str
    elapsed_seconds: float
    bytes_processed: int = 0
    members_processed: int = 0
    source_bytes: int = 0
    output_bytes: int = 0
    peak_rss_kib: int | None = None
    cpu_user_seconds: float = 0.0
    cpu_system_seconds: float = 0.0

    @property
    def throughput_mib_s(self) -> float:
        return (self.bytes_processed / 1048576 / self.elapsed_seconds) if self.elapsed_seconds else 0.0

    @property
    def cpu_seconds(self) -> float:
        return self.cpu_user_seconds + self.cpu_system_seconds

    def __str__(self) -> str:
        return self.format

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.format == other
        if isinstance(other, OperationResult):
            return self.to_dict() == other.to_dict()
        return NotImplemented

    def to_dict(self) -> dict:
        data = asdict(self)
        data["throughput_mib_s"] = round(self.throughput_mib_s, 3)
        data["cpu_seconds"] = round(self.cpu_seconds, 6)
        return data
