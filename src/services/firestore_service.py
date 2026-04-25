"""Google Cloud Firestore service wrapper for VoteReady."""

import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from google.cloud import firestore

from src.config import settings

logger = logging.getLogger(__name__)

class FirestoreService:
    """Wrapper for Google Cloud Firestore.
    
    Handles user profiles, checklist progress, and response caching.
    All operations are async-safe and handle errors gracefully.
    """
    
    def __init__(self):
        """Initialize Firestore client and define collections.
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            self.client = firestore.AsyncClient(project=settings.google_cloud_project)
            self.users_coll = self.client.collection(settings.firestore_collection_users)
            self.checklists_coll = self.client.collection(settings.firestore_collection_checklist)
            self.cache_coll = self.client.collection(settings.firestore_collection_cache)
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            self.client = None
    
    # ---- User Profile Operations ----
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user profile in Firestore.
        
        Args:
            user_data: Dict with name, age, state, district, 
                      voter_id, language, created_at.
                      
        Returns:
            Generated user_id string.
        """
        if not self.client:
            logger.warning("Firestore client not initialized. Cannot create user.")
            return str(uuid.uuid4())
            
        user_id = str(uuid.uuid4())
        user_data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        try:
            await self.users_coll.document(user_id).set(user_data)
            return user_id
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return user_id
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile by ID.
        
        Args:
            user_id: The user's unique identifier.
            
        Returns:
            User dict or None if not found.
        """
        if not self.client:
            return None
            
        try:
            doc = await self.users_coll.document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields in a user profile.
        
        Args:
            user_id: The user's unique identifier.
            updates: Dict of fields to update.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.client:
            return False
            
        try:
            await self.users_coll.document(user_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return False
    
    # ---- Checklist Operations ----
    
    async def get_checklist(self, user_id: str) -> Dict[str, Any]:
        """Get user's voter readiness checklist progress.
        
        Args:
            user_id: The user's unique identifier.
            
        Returns:
            Dict with checklist items and completion status.
            Returns default checklist if none exists.
        """
        default_checklist = {
            "items": {
                "check_registration": {"title": "Check if you're on the electoral roll", "completed": False},
                "get_voter_id": {"title": "Get your Voter ID (EPIC)", "completed": False},
                "find_booth": {"title": "Find your polling booth", "completed": False},
                "prepare_documents": {"title": "Prepare your ID documents", "completed": False},
                "know_candidates": {"title": "Know your candidates", "completed": False},
                "polling_day_ready": {"title": "Know polling day procedures", "completed": False}
            }
        }
        
        if not self.client:
            return default_checklist
            
        try:
            doc = await self.checklists_coll.document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            
            # Create default if missing
            await self.checklists_coll.document(user_id).set(default_checklist)
            return default_checklist
        except Exception as e:
            logger.error(f"Error retrieving checklist for user {user_id}: {str(e)}")
            return default_checklist
    
    async def update_checklist_item(
        self, 
        user_id: str, 
        item_id: str, 
        completed: bool
    ) -> bool:
        """Update a single checklist item's completion status.
        
        Args:
            user_id: The user's unique identifier.
            item_id: The checklist item identifier.
            completed: Whether the item is completed.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.client:
            return False
            
        try:
            await self.checklists_coll.document(user_id).update({
                f"items.{item_id}.completed": completed
            })
            return True
        except Exception as e:
            logger.error(f"Error updating checklist item {item_id} for user {user_id}: {str(e)}")
            return False
    
    # ---- Cache Operations ----
    
    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached Gemini response if not expired.
        
        Args:
            cache_key: The cache key string.
            
        Returns:
            Cached response dict or None if expired/missing.
        """
        if not self.client:
            return None
            
        try:
            doc = await self.cache_coll.document(cache_key).get()
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            expires_at = data.get("ttl_expires_at")
            
            if expires_at and expires_at > datetime.now(timezone.utc).timestamp():
                return data.get("response")
            return None
        except Exception as e:
            logger.error(f"Error retrieving cache for {cache_key}: {str(e)}")
            return None
    
    async def set_cached_response(
        self, 
        cache_key: str, 
        response: Dict[str, Any], 
        ttl_seconds: int = 86400
    ) -> None:
        """Store a Gemini response in cache with TTL.
        
        Args:
            cache_key: The cache key string.
            response: The response data to cache.
            ttl_seconds: Time-to-live in seconds (default 24 hours).
        """
        if not self.client:
            return
            
        try:
            now = datetime.now(timezone.utc)
            expires_at = now.timestamp() + ttl_seconds
            
            data = {
                "response": response,
                "created_at": now.isoformat(),
                "ttl_expires_at": expires_at
            }
            await self.cache_coll.document(cache_key).set(data)
        except Exception as e:
            logger.error(f"Error setting cache for {cache_key}: {str(e)}")

_firestore_service: Optional[FirestoreService] = None

def get_firestore_service() -> FirestoreService:
    """Get or create the Google Cloud Firestore service singleton instance.
    
    Args:
        None
        
    Returns:
        The shared FirestoreService instance.
    """
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service
