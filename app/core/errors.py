class AppError(Exception):
    """Base app domain error."""


class ValidationError(AppError):
    """Validation level issue."""


class PdfProcessingError(AppError):
    """Raised when PDF cannot be reliably parsed."""


class LocalModelUnavailableError(AppError):
    """Raised when local Ollama model is unavailable."""


class NotFoundError(AppError):
    """Raised when entity is not found."""
