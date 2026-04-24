"""Google Cloud Translation API service wrapper for VoteReady."""

import logging
from typing import List, Optional

from google.cloud import translate_v3

from src.config import settings

logger = logging.getLogger(__name__)

class TranslateService:
    """Wrapper for Google Cloud Translation API.
    
    Translates UI text and dynamic content between English and Hindi.
    Uses pre-translated static content where available,
    falls back to API for dynamic content only.
    """
    
    def __init__(self):
        """Initialize Translation client with project config."""
        try:
            self.client = translate_v3.TranslationServiceClient()
            self.parent = settings.google_translate_parent
        except Exception as e:
            logger.error(f"Failed to initialize Translation client: {str(e)}")
            self.client = None
    
    async def translate_text(
        self,
        text: str,
        target_language: str = "hi",
        source_language: str = "en"
    ) -> str:
        """Translate text between English and Hindi.
        
        Args:
            text: Text to translate.
            target_language: Target language code ("hi" or "en").
            source_language: Source language code ("en" or "hi").
            
        Returns:
            Translated text string.
            Returns original text if translation fails.
        """
        if source_language == target_language:
            return text
            
        if not self.client:
            logger.warning("Translate client not initialized. Returning original text.")
            return text
            
        try:
            response = self.client.translate_text(
                request={
                    "parent": self.parent,
                    "contents": [text],
                    "mime_type": "text/plain",
                    "source_language_code": source_language,
                    "target_language_code": target_language,
                }
            )
            return response.translations[0].translated_text
        except Exception as e:
            logger.warning(f"Translation failed: {str(e)}. Falling back to original.")
            return text
    
    async def translate_batch(
        self,
        texts: List[str],
        target_language: str = "hi"
    ) -> List[str]:
        """Translate multiple texts in a single API call.
        
        Args:
            texts: List of strings to translate.
            target_language: Target language code.
            
        Returns:
            List of translated strings (same order as input).
        """
        if not texts:
            return []
            
        if target_language == "en":  # Assuming source is English
            return texts
            
        if not self.client:
            logger.warning("Translate client not initialized. Returning original texts.")
            return texts
            
        try:
            response = self.client.translate_text(
                request={
                    "parent": self.parent,
                    "contents": texts,
                    "mime_type": "text/plain",
                    "source_language_code": "en",
                    "target_language_code": target_language,
                }
            )
            return [translation.translated_text for translation in response.translations]
        except Exception as e:
            logger.warning(f"Batch translation failed: {str(e)}. Falling back to originals.")
            return texts

_translate_service: Optional[TranslateService] = None

def get_translate_service() -> TranslateService:
    """Get or create the Translate service singleton."""
    global _translate_service
    if _translate_service is None:
        _translate_service = TranslateService()
    return _translate_service
