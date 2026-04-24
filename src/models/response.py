"""Universal API response model and helper functions."""

from datetime import datetime, timezone
from typing import Literal, Dict, List, Any, Optional
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    """Detailed error information for the response."""
    code: str
    message: str

class APIResponse(BaseModel):
    """Standardized API response structure."""
    status: Literal["success", "error"]
    data: Optional[Dict[str, Any] | List[Any]] = None
    error: Optional[ErrorDetail] = None
    timestamp: str
    language: Literal["en", "hi"] = "en"

def success_response(data: Dict[str, Any] | List[Any], language: str = "en") -> dict:
    """Create a standardized success response.
    
    Args:
        data: The response data payload.
        language: Response language code (en/hi).
        
    Returns:
        dict: Standardized success response dictionary.
    """
    return {
        "status": "success",
        "data": data,
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "language": language
    }

def error_response(code: str, message: str, language: str = "en") -> dict:
    """Create a standardized error response.
    
    Args:
        code: Error classification code.
        message: Human-readable error description.
        language: Response language code (en/hi).
        
    Returns:
        dict: Standardized error response dictionary.
    """
    return {
        "status": "error",
        "data": None,
        "error": {"code": code, "message": message},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "language": language
    }
