import httpx
import os
import time
import openai
import re
import asyncio
from difflib import SequenceMatcher
import difflib
from utils.cache_manager import cache_manager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
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
        logger.info(f"Starting recommendations for locations: {location}")
        recommendations = {}
        start_time = time.time()

        for loc in location:
            logger.info(f"\nProcessing location: {loc}")
            loc_start_time = time.time()

            # Try to get cached geocoding result
            lat_lng = cache_manager.get_cached('geocode', loc)
            if lat_lng:
                logger.info(f"Cache HIT: Geocoding for {loc}")
            else:
                logger.info(f"Cache MISS: Geocoding for {loc}")
                lat_lng = await self._get_lat_lng(loc)
                if lat_lng:
                    cache_manager.set_cached('geocode', loc, lat_lng)
                    logger.info(f"Cached geocoding result for {loc}")

            if not lat_lng:
                logger.warning(f"Failed to get coordinates for {loc}, skipping")
                continue

            # Try to get cached places results for restaurants
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
            all_attractions = []
            for attr_type in self.attraction_types:
                cache_key = f"{lat_lng}_{attr_type}"
                attractions = cache_manager.get_cached('places', cache_key)
                if attractions:
                    logger.info(f"Cache HIT: {attr_type} for {loc}")
                else:
                    logger.info(f"Cache MISS: {attr_type} for {loc}")
                    attractions = await self._fetch_places(lat_lng, attr_type)
                    if attractions:
                        cache_manager.set_cached('places', cache_key, attractions)
                        logger.info(f"Cached {len(attractions)} {attr_type} for {loc}")
                if attractions:
                    all_attractions.extend(attractions)

            # Process attractions to get unique ones and limit to 5
            unique_attractions = {p["place_id"]: p for p in all_attractions}.values()
            attractions = list(unique_attractions)[:5]

            # Use OpenAI to refine recommendations
            best_restaurants = self._rank_with_ai(restaurants, "restaurants")
            best_hotels = self._rank_with_ai(hotels, "hotels")

            # Fetch detailed information for each place
            restaurant_details = await self._get_place_details_async(best_restaurants)
            hotel_details = await self._get_place_details_async(best_hotels)
            attraction_details = await self._get_place_details_async(attractions)

            # Create the recommendations dictionary for this location
            recommendations[loc] = {
                "restaurants": restaurant_details,
                "hotels": hotel_details,
                "attractions": attraction_details
            }

            loc_end_time = time.time()
            logger.info(f"Completed processing {loc} in {loc_end_time - loc_start_time:.2f} seconds")
            logger.info(f"Results for {loc}:")
            logger.info(f" - Restaurants: {len(restaurant_details)}")
            logger.info(f" - Hotels: {len(hotel_details)}")
            logger.info(f" - Attractions: {len(attraction_details)}")

        end_time = time.time()
        logger.info(f"\nTotal processing time: {end_time - start_time:.2f} seconds")
        logger.info(f"Cache sizes: {cache_manager.get_cache_size()}")

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
            
    async def _get_place_details_async(self, places):
        """
        Get detailed information for places with caching
        """
        results = []
        for place in places:
                if not place.get("place_id"):
                    continue
                
                # Try to get cached place details
                cache_key = f"place_details_{place['place_id']}"
                cached_details = cache_manager.get_cached('places', cache_key)
                if cached_details:
                    logger.info(f"Cache HIT: Place details for {place.get('name', 'Unknown')}")
                    results.append(cached_details)
                    continue

                logger.info(f"Cache MISS:  Place details for {place.get('name', 'Unknown')}")
                try:
                    response = await self.http_client.get(
                        self.details_url,
                        params={
                            "place_id": place["place_id"],
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
                            "coords": place.get("coords"),
                            "place_id": place["place_id"]
                        }

                        #Cache the place details
                        cache_manager.set_cached('places', cache_key, place_details)
                        logger.info(f"Cached place details for {place_details['name']}")
                        results.append(place_details)
                except Exception as e:
                    logger.error(f"Error getting place details for {place.get('name', 'Unknown')}: {str(e)}")
                    continue

        return results
    
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