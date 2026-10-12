class PiriError(Exception):
    """Base exception for piri."""


class BackendError(PiriError):
    """Backend execution or capability failure."""


class FormatError(PiriError):
    """Unsupported or invalid archive format."""


class PolicyError(PiriError):
    """Archive/resource/overwrite policy violation."""


class IntegrityError(PiriError):
    """Post-extraction integrity verification failure."""
