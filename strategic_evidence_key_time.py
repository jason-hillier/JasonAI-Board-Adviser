"""Timestamp validation for Macian signing-key governance."""

from datetime import datetime, timezone


def parse_key_timestamp(value: str) -> datetime:
    """Parse a timezone-aware ISO 8601 timestamp into UTC."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("A non-empty timestamp is required.")

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid ISO 8601 timestamp.") from exc

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone.")

    return parsed.astimezone(timezone.utc)
