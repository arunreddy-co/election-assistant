"""Google Maps API service wrapper for VoteReady."""

import logging
from typing import List, Dict, Any, Optional

import googlemaps

from src.config import settings

logger = logging.getLogger(__name__)

class MapsService:
    """Wrapper for Google Maps API to find polling booths.
    
    Uses the Places API to search for polling stations
    near a user's location or within their district.
    """
    
    def __init__(self):
        """Initialize Google Maps client with API key from config."""
        try:
            self.client = googlemaps.Client(key=settings.google_maps_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {str(e)}")
            self.client = None
    
    async def find_polling_booths(
        self,
        district: str,
        state: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find polling booths near the user's district.
        
        Args:
            district: User's district name.
            state: User's state name.
            limit: Maximum number of results (default 5).
            
        Returns:
            List of dicts with keys: name, address, latitude, longitude, place_id
            Empty list if no results found.
        """
        if not self.client:
            logger.warning("Maps client not initialized.")
            return []
            
        query = f"polling booth {district} {state} India"
        
        try:
            places_result = self.client.places(query=query)
            
            results = []
            if places_result and "results" in places_result:
                for place in places_result["results"][:limit]:
                    results.append({
                        "name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"],
                        "place_id": place.get("place_id")
                    })
            return results
        except Exception as e:
            logger.error(f"Error finding polling booths: {str(e)}")
            return []
    
    async def get_directions_url(
        self,
        destination_lat: float,
        destination_lng: float
    ) -> str:
        """Generate Google Maps directions URL for a polling booth.
        
        Args:
            destination_lat: Booth latitude.
            destination_lng: Booth longitude.
            
        Returns:
            Google Maps URL string that opens directions.
        """
        return f"https://www.google.com/maps/dir/?api=1&destination={destination_lat},{destination_lng}"

_maps_service: Optional[MapsService] = None

def get_maps_service() -> MapsService:
    """Get or create the Maps service singleton."""
    global _maps_service
    if _maps_service is None:
        _maps_service = MapsService()
    return _maps_service
