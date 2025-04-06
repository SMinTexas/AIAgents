import httpx
import os
import time
import openai
import re
import asyncio
from difflib import SequenceMatcher
import difflib
import sys
from pathlib import Path
# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
from utils.cache_manager import cache_manager
import logging


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

def normalize(name):
    return re.sub(r"[^\w\s]", "", name).lower().strip()

class RecommendationAgent:
    def __init__(self):
        """ Initialize Google Places API """
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2025-01-01-preview"
        )
        self.attraction_types=["museum","tourist_attraction","shopping_mall","zoo","casino","aquarium"]
        self.base_places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

        # Create an async client with explicit proxy settings
        self.http_client = httpx.AsyncClient(
            verify=False,
            proxies=None,
            timeout=30.0
        )

        logger.info("RecommendationAgent initialized")

    async def get_recommendations(self, location):
        """ 
        Fetch recommendations for restaurants, hotels, and attractions 
        """
        total_start_time = time.time()
        logger.info(f"Starting recommendations for locations: {location}")
        recommendations = {}

        for loc in location:
            loc_start_time = time.time()
            logger.info(f"\nProcessing location: {loc}")

            # Try to get cached geocoding result
            geocode_start = time.time()
            lat_lng = cache_manager.get_cached('geocode', loc)
            if lat_lng:
                logger.info(f"Cache HIT: Geocoding for {loc}")
            else:
                logger.info(f"Cache MISS: Geocoding for {loc}")
                lat_lng = await self._get_lat_lng(loc)
                if lat_lng:
                    cache_manager.set_cached('geocode', loc, lat_lng)
                    logger.info(f"Cached geocoding result for {loc}")
            geocode_time = time.time() - geocode_start
            logger.info(f"Geocoding took {geocode_time:.2f} seconds")

            if not lat_lng:
                logger.warning(f"Failed to get coordinates for {loc}, skipping")
                continue

            # Try to get cached places results for restaurants
            places_start = time.time()
            cache_key = f"{lat_lng}_restaurant"
            restaurants = cache_manager.get_cached('places', cache_key)
            if restaurants:
                logger.info(f"Cache HIT:  Restaurants for {loc}")
            else:
                logger.info(f"Cache MISS: Restaurants for {loc}")
                restaurants = await self._fetch_places(lat_lng, "restaurant")
                if restaurants:
                    cache_manager.set_cached('places', cache_key, restaurants)
                    logger.info(f"Cached {len(restaurants)} restaurants for {loc}")

            # Try to get cached places results for hotels
            cache_key = f"{lat_lng}_lodging"
            hotels = cache_manager.get_cached('places', cache_key)
            if hotels:
                logger.info(f"Cache HIT:  Hotels for {loc}")
            else:
                logger.info(f"Cache MISS:  Hotels for {loc}")
                hotels = await self._fetch_places(lat_lng, "lodging")
                if hotels:
                    cache_manager.set_cached('places', cache_key, hotels)
                    logger.info(f"Cached {len(hotels)} hotels for {loc}")

            # Get attractions across multiple categories
            attractions_start = time.time()
            attractions = []
            for attraction_type in self.attraction_types:
                cache_key = f"{lat_lng}_{attraction_type}"
                cached_attractions = cache_manager.get_cached('places', cache_key)
                if cached_attractions:
                    logger.info(f"Cache HIT: {attraction_type} for {loc}")
                    attractions.extend(cached_attractions)
                else:
                    logger.info(f"Cache MISS: {attraction_type} for {loc}")
                    type_attractions = await self._fetch_places(lat_lng, attraction_type)
                    if type_attractions:
                        cache_manager.set_cached('places', cache_key, type_attractions)
                        logger.info(f"Cached {len(type_attractions)} {attraction_type} for {loc}")
                        attractions.extend(type_attractions)

            attractions_time = time.time() - attractions_start
            logger.info(f"Attractions fetching took {attractions_time:.2f} seconds")

            # Get details for all places
            details_start = time.time()
            all_places = []
            if restaurants:
                all_places.extend(restaurants)
            if hotels:
                all_places.extend(hotels)
            if attractions:
                all_places.extend(attractions)

            place_details = []
            for place in all_places:
                cache_key = f"details_{place['place_id']}"
                details = cache_manager.get_cached('details', cache_key)
                if details:
                    logger.info(f"Cache HIT:  Details for place {place['place_id']}")
                    place_details.append(details)
                else:
                    logger.info(f"Cache MISS: Details for place {place['place_id']}")
                    details = await self._get_place_details(place['place_id'])
                    if details:
                        cache_manager.set_cached('details', cache_key, details)
                        logger.info(f"Cached details for place {place['place_id']}")
                        place_details.append(details)
            
            details_time = time.time() - details_start
            logger.info(f"Place details fetching took {details_time:.2f} seconds")

            recommendations[loc] = {
                "restaurants": restaurants,
                "hotels": hotels,
                "attractions": attractions
            }

            loc_time = time.time() - loc_start_time
            logger.info(f"Total time for location {loc}: {loc_time:.2f} seconds")

        total_time = time.time() - total_start_time
        logger.info(f"\nTotal time for all locations: {total_time:.2f} seconds")

        return recommendations
    
    async def _get_lat_lng(self, address):
        """
        Get latitude and longitude for an address with caching
        """
        try:
            response = await self.http_client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": address, "key": self.google_api_key}
            )
            result = response.json()
            if result["results"]:
                loc = result["results"][0]["geometry"]["location"]
                return f"{loc['lat']},{loc['lng']}"
        except Exception as e:
            logger.error(f"Error getting lat/lng for {address}: {str(e)}")

        return None
    
    async def _fetch_places(self, location, place_type):
        """
        Fetch places with caching
        """
        try:
           response = await self.http_client.get(
               self.base_places_url,
               params={
                   "location": location,
                   "radius": 2000,
                   "type": place_type,
                   "key": self.google_api_key
               }
           )
           result = response.json()
           return [{
               "name": p["name"],
               "place_id": p.get("place_id"),
               "coords": [p["geometry"]["location"]["lat"], p["geometry"]["location"]["lng"]],
           } for p in result.get("results", []) if p.get("place_id")] 
        except Exception as e:
            logger.error(f"Error fetching places for {location}: {str(e)}")
            return []
            
    async def _get_place_details(self, place_id):
        """
        Get detailed information for for a single place with caching
        """
        try:
                
            # Try to get cached place details
            cache_key = f"details_{'place_id'}"
            cached_details = cache_manager.get_cached('details', cache_key)
            if cached_details:
                logger.info(f"Cache HIT:  Place details for {place.get('name', 'Unknown')}")
                return cached_details

            logger.info(f"Cache MISS:  Place details for {place_id}")
            response = await self.http_client.get(
                self.details_url,
                params={
                    "place_id": place_id,
                    "fields": "name,formatted_address,formatted_phone_number,rating,opening_hours",
                    "key": self.google_api_key
                }
            )
            result = response.json()
            if "result" in result:
                details = result["result"]
                place_details = {
                    "name": details.get("name", "N/A"),
                    "address": details.get("formatted_address", "N/A"),
                    "phone_number": details.get("formatted_phone_number", "N/A"),
                    "rating": details.get("rating", "N/A"),
                    "opening_hours": details.get("opening_hours", {}).get("weekday_text", "N/A"),
                    "place_id": place_id
                }

                # Cache the place details
                cache_manager.set_cached('details', cache_key, place_details)
                logger.info(f"Cached place details for {place_details['name']}")
                return place_details
        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {str(e)}")

        return None
    
    def _rank_with_ai(self, places, category):
        """ 
        Use OpenAI to rank places based on user preferences 
        """
        if not places:
            return []
        
        # Create the AI prompt
        prompt = f"Rank these {category} based on reviews and relevance:\n"
        for p in places:
            prompt += f"- {p['name']} (Rating: {p.get('rating', 'N/A')})\n"

        # Call OpenAI to get ranking
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that ranks restaurants, hotels, and attractions based on user preferences."},
                {"role": "user", "content": prompt}
            ]
        )

        # Initialize variables for processing the AI response
        ranked_places = []
        matched_names = set()

        # Get the AI's response and split it into lines
        ai_response = response.choices[0].message.content
        lines = ai_response.split("\n")

        # Create a dictionary of normalized place names for matching
        normalized_places = {normalize(p["name"]): p for p in places}

        # Process each line of the AI response
        for line in lines:
            # Skip lines that don't start with a number
            if not re.match(r"^\d+[\.\)]", line.strip()):
                continue

            # Extract the place name from the line
            match = re.search(r"^\s*[\d•\-]+[.)\s-]*\**(.*?)\**(?:\s*\(|$)", line)
            if not match: 
                continue

            # Clean and normalize the extracted name
            cleaned_name = normalize(match.group(1))
            if not cleaned_name:
                continue

            # Find the best matching place from our list
            close_matches = difflib.get_close_matches(cleaned_name, normalized_places.keys(), n=1, cutoff=0.7)

            # If we found a match, add it to our ranked places
            if close_matches:
                best_match = close_matches[0]
                place = normalized_places[best_match]
                if place["name"] not in matched_names:
                    matched_names.add(place["name"])
                    ranked_places.append(place)

            # Stop after getting 5 places
            if len(ranked_places) >= 5:
                break
        
        # If no matches were found, return the top 5 raw results
        if not ranked_places:
            logger.warning(f"No matches found via AI for {category}. Using top 5 raw results")
            return places[:5]
        
        return ranked_places