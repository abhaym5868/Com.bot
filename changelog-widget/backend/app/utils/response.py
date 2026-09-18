"""
utils/response.py
-----------------
Helpers to build consistent JSON responses throughout the API.

Every endpoint returns the same envelope shape:

Success:
    {
        "success": true,
        "message": "...",
        "data": { ... }          # or null
    }

Error (handled via HTTPException in main.py):
    {
        "success": false,
        "message": "...",
        "data": null
    }

This makes the frontend easy to write — it always knows where to look.
"""

from typing import Any


def success_response(message: str, data: Any = None) -> dict:
    """Return a standard success envelope."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, data: Any = None) -> dict:
    """Return a standard error envelope (used in exception handlers)."""
    return {
        "success": False,
        "message": message,
        "data": data,
    }
