"""
Shared utilities for the API
"""

from typing import Any

# Helper function to safely handle SQLAlchemy column values
def safe_len(value: Any) -> int:
    """Safely get length of a value that might be None"""
    return len(value) if value is not None else 0

# Helper function to get actual values from SQLAlchemy objects
def get_session_value(session_obj: Any, attr_name: str) -> Any:
    """Get the actual value from a SQLAlchemy session object"""
    return getattr(session_obj, attr_name)