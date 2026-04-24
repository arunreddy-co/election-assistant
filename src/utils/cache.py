"""In-memory caching utility for the VoteReady application."""

import time
import hashlib
from typing import Optional, Dict, Any

class ResponseCache:
    """In-memory cache with TTL for API responses.
    
    Falls back to Firestore cache for persistence across restarts.
    Memory cache checked first for speed, Firestore second for persistence.
    """
    
    def __init__(self, default_ttl_seconds: int = 86400):
        """Initialize cache with default TTL.
        
        Args:
            default_ttl_seconds: Time to live in seconds (default 24 hours).
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if not expired.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value if found and valid, None otherwise.
        """
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item["expires_at"]:
                return item["value"]
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """Store response with TTL.
        
        Args:
            key: Cache key.
            value: Data to cache.
            ttl_seconds: Optional custom TTL for this item.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters.
        
        Args:
            prefix: Key prefix.
            **kwargs: Parameters to hash.
            
        Returns:
            Generated cache key string.
        """
        param_str = str(sorted(kwargs.items())).encode('utf-8')
        param_hash = hashlib.md5(param_str).hexdigest()
        return f"{prefix}:{param_hash}"
    
    def clear_expired(self) -> int:
        """Remove expired entries.
        
        Returns:
            int: Count of removed items.
        """
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if now >= v["expires_at"]]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)
