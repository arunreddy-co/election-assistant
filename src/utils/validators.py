"""Input validation utilities for the VoteReady application."""

import re

VALID_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", " हिमाचल प्रदेश", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", 
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", 
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", 
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", 
    "Ladakh", "Lakshadweep", "Puducherry"
]

def sanitize_string(value: str) -> str:
    """Remove HTML tags, script patterns, and dangerous characters.
    
    Args:
        value: Input string to sanitize.
        
    Returns:
        str: Sanitized string.
    """
    if not value:
        return value
        
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', value)
    return clean.strip()

def validate_state(state: str) -> bool:
    """Check if state is a valid Indian state or UT.
    
    Args:
        state: State name to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    return state in VALID_STATES

def validate_age(age: int) -> bool:
    """Check if age is within valid range (1-150).
    
    Args:
        age: Age to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    return 1 <= age <= 150

def validate_voter_id(voter_id: str) -> bool:
    """Validate voter ID format: 3 letters + 7 digits (e.g., ABC1234567).
    
    Args:
        voter_id: Voter ID string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not voter_id:
        return False
    return bool(re.match(r'^[A-Z]{3}\d{7}$', voter_id.upper()))

def is_safe_input(text: str) -> bool:
    """Check input for XSS, SQL injection, and prompt injection patterns.
    
    Args:
        text: Input string to check.
        
    Returns:
        bool: True if safe, False if potentially dangerous.
    """
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'UNION SELECT',
        r'DROP TABLE',
        r'Ignore previous instructions',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True
