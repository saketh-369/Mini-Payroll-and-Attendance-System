"""Reusable HTTP exception helpers."""

from fastapi import HTTPException, status


def not_found(detail: str = "Resource not found"):
    """Raise a 404 Not Found."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def bad_request(detail: str = "Bad request"):
    """Raise a 400 Bad Request."""
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def conflict(detail: str = "Conflict"):
    """Raise a 409 Conflict."""
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
