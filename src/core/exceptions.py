"""Custom exceptions for GuardianEye."""


class GuardianEyeException(Exception):
    """Base exception for all GuardianEye errors."""
    pass


class LLMProviderError(GuardianEyeException):
    """Raised when LLM provider configuration or execution fails."""
    pass


class AgentExecutionError(GuardianEyeException):
    """Raised when agent execution fails."""
    pass


class StateManagementError(GuardianEyeException):
    """Raised when state persistence or retrieval fails."""
    pass


class AuthenticationError(GuardianEyeException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(GuardianEyeException):
    """Raised when user lacks permission for an action."""
    pass


class ValidationError(GuardianEyeException):
    """Raised when input validation fails."""
    pass


class DatabaseError(GuardianEyeException):
    """Raised when database operations fail."""
    pass
