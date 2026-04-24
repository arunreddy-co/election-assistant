"""Pydantic request models with strict validation."""

from typing import Literal, Optional
from pydantic import BaseModel, field_validator
from src.utils.validators import (
    sanitize_string, 
    validate_state, 
    validate_age, 
    validate_voter_id,
    is_safe_input
)

class OnboardRequest(BaseModel):
    """Request model for user onboarding."""
    name: str
    age: int
    state: str
    district: str
    voter_id: Optional[str] = None
    language: Literal["en", "hi"] = "en"

    @field_validator("name", "district")
    @classmethod
    def validate_string_fields(cls, v: str) -> str:
        """Sanitize and validate basic string fields."""
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Field length must be between 2 and 100 characters.")
        sanitized = sanitize_string(v)
        if not is_safe_input(sanitized):
            raise ValueError("Input contains unsafe content.")
        if not sanitized:
            raise ValueError("Field cannot be empty or only whitespace.")
        return sanitized

    @field_validator("age")
    @classmethod
    def validate_user_age(cls, v: int) -> int:
        """Validate user age is within range."""
        if not validate_age(v):
            raise ValueError("Age must be between 1 and 150.")
        return v

    @field_validator("state")
    @classmethod
    def validate_user_state(cls, v: str) -> str:
        """Validate state against known list."""
        if not validate_state(v):
            raise ValueError("Invalid Indian state or UT.")
        return v

    @field_validator("voter_id")
    @classmethod
    def validate_user_voter_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional voter ID format."""
        if v is not None and not validate_voter_id(v):
            raise ValueError("Voter ID must be 3 letters followed by 7 digits.")
        return v


class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    message: str
    user_id: str
    language: Literal["en", "hi"] = "en"
    context_screen: Optional[str] = None

    @field_validator("message")
    @classmethod
    def validate_chat_message(cls, v: str) -> str:
        """Sanitize and validate chat message."""
        if len(v) < 1 or len(v) > 500:
            raise ValueError("Message length must be between 1 and 500 characters.")
        sanitized = sanitize_string(v)
        if not is_safe_input(sanitized):
            raise ValueError("Input contains unsafe content.")
        if not sanitized:
            raise ValueError("Message cannot be empty.")
        return sanitized

    @field_validator("user_id")
    @classmethod
    def validate_chat_user_id(cls, v: str) -> str:
        """Validate user ID is not empty."""
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty.")
        return v.strip()


class ChecklistUpdateRequest(BaseModel):
    """Request model for updating voter checklist."""
    user_id: str
    item_id: str
    completed: bool

    @field_validator("user_id", "item_id")
    @classmethod
    def validate_id_fields(cls, v: str) -> str:
        """Validate ID fields are not empty."""
        if not v or not v.strip():
            raise ValueError("ID fields cannot be empty.")
        return v.strip()
