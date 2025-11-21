"""Custom validators for input validation."""

import re


def is_valid_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid, False otherwise
    """
    # Session IDs should be alphanumeric with optional hyphens/underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, session_id))


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Truncate to max length
    text = text[:max_length]

    # Remove potential script tags and other dangerous patterns
    # This is a basic sanitization - enhance for production use
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    return text.strip()


def validate_agent_name(agent_name: str) -> bool:
    """
    Validate agent name format.

    Args:
        agent_name: Agent name to validate

    Returns:
        True if valid, False otherwise
    """
    # Agent names should be lowercase alphanumeric with underscores
    pattern = r"^[a-z0-9_]+$"
    return bool(re.match(pattern, agent_name))
