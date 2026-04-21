"""
utils/helpers.py — Shared utility functions.

RESPONSIBILITY: Generic, reusable helpers with no domain knowledge.
  These functions do not import from app.models or app.services.
  They are tools that any layer can use.

Current helpers:
  • paginate_params  — normalise skip/limit query params
  • sanitise_string  — strip & collapse whitespace

Add more helpers here as the project grows (e.g. format_datetime).
"""


def paginate_params(skip: int = 0, limit: int = 100) -> tuple[int, int]:
    """
    Clamp pagination parameters to safe bounds.

    Returns (skip, limit) so callers can unpack directly:
        skip, limit = paginate_params(skip, limit)

    Rules:
      • skip  must be >= 0           (no negative offsets)
      • limit must be between 1–500  (prevent huge queries)
    """
    skip = max(0, skip)
    limit = max(1, min(limit, 500))
    return skip, limit


def sanitise_string(value: str | None) -> str | None:
    """
    Strip leading/trailing whitespace and collapse internal spaces.

    Returns None if the input is None or becomes empty after stripping.

    Examples:
        sanitise_string("  hello   world  ")  →  "hello world"
        sanitise_string("   ")                →  None
        sanitise_string(None)                 →  None
    """
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned if cleaned else None
