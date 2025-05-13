import httpx
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
import googlemaps

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from utils.cache_manager import cache_manager
import logging

# Set up logging with a more concise format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

def normalize(name):
    return re.sub(r"[^\w\s]", "", name).lower().strip()

class RecommendationAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key not found")
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.http_client = httpx.AsyncClient()

    async def get_recommendations(self, locations, preferences):
        """Get recommendations for each location based on preferences"""
        print(f"\nGetting recommendations for locations: {locations}")
        print(f"With preferences: {preferences}")
        
        recommendations = {}
        
        for location in locations:
            print(f"\nProcessing location: {location}")
            try:
                # Get coordinates for the location
                geocode_result = self.gmaps.geocode(location)
                if not geocode_result:
                    print(f"Could not geocode location: {location}")
                    continue
                
                location_data = geocode_result[0]
                lat = location_data['geometry']['location']['lat']
                lng = location_data['geometry']['location']['lng']
                
                print(f"Coordinates for {location}: {lat}, {lng}")
                
                # Initialize recommendations for this location
                recommendations[location] = {
                    "hotels": [],
                    "restaurants": [],
                    "attractions": []
                }
                
                # Always get hotels and restaurants
                print(f"Getting hotels for {location}")
                hotels = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=5000,
                    type='lodging',
                    rank_by='rating'
                )
                
                if hotels and 'results' in hotels:
                    recommendations[location]["hotels"] = hotels['results'][:5]
                    print(f"Found {len(hotels['results'])} hotels")
                
                print(f"Getting restaurants for {location}")
                restaurants = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=5000,
                    type='restaurant',
                    rank_by='rating'
                )
                
                if restaurants and 'results' in restaurants:
                    recommendations[location]["restaurants"] = restaurants['results'][:5]
                    print(f"Found {len(restaurants['results'])} restaurants")
                
                # Get attractions based on preferences
                for preference in preferences:
                    print(f"Getting {preference} for {location}")
                    places = self.gmaps.places_nearby(
                        location=(lat, lng),
                        radius=5000,
                        type=preference,
                        rank_by='rating'
                    )
                    
                    if places and 'results' in places:
                        recommendations[location]["attractions"].extend(places['results'][:5])
                        print(f"Found {len(places['results'])} {preference}")
                
            except Exception as e:
                print(f"Error getting recommendations for {location}: {str(e)}")
                continue
        
        print(f"\nFinal recommendations structure: {recommendations}")
        return recommendations

    async def _get_lat_lng(self, address):
        """ Get latitude and longitude for an address with caching """
        try:
            response = await self.http_client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": address, "key": self.api_key}
            )
            result = response.json()
            if result["results"]:
                loc = result["results"][0]["geometry"]["location"]
                return f"{loc['lat']},{loc['lng']}"
        except Exception as e:
            logger.error(f"Error getting lat/lng for {address}: {str(e)}")
        return None
    
    async def _fetch_places(self, location, place_type):
        """ Fetch places with caching """
        try:
            response = await self.http_client.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params={
                    "location": location,
                    "radius": 20000,
                    "type": place_type,
                    "key": self.api_key
                }
            )
            result = response.json()
            # Limit to 5 places per category
            places = [{
                "name": p["name"],
                "place_id": p.get("place_id"),
                "coords": [p["geometry"]["location"]["lat"], p["geometry"]["location"]["lng"]],
            } for p in result.get("results", []) if p.get("place_id")]
            return places[:5]  # Limit to 5 places
        except Exception as e:
            logger.error(f"Error fetching places for {location}: {str(e)}")
            return []

    async def _get_place_details(self, place_id):
        """ Get detailed information for a single place with caching """
        try:
            # Try to get cached place details
            cache_key = f"details_{place_id}"
            cached_details = cache_manager.get_cached('details', cache_key)
            if cached_details:
                logger.debug(f"Cache HIT: Place details for {place_id}")
                return cached_details

            logger.debug(f"Cache MISS: Place details for {place_id}")
            response = await self.http_client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "name,formatted_address,formatted_phone_number,rating,opening_hours",
                    "key": self.api_key
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
                logger.debug(f"Cached place details for {place_details['name']}")
                return place_details
        except Exception as e:
            logger.error(f"Error getting place details for place_id {place_id}: {str(e)}")
        return None

    def _rank_with_ai(self, places, category):
        """ 
        Use OpenAI to rank places based on user preferences 
        """
        if not places:
            return []
        
        # Create the prompt for the AI
        prompt = f"Rank these {category} based on reviews and relevance:\n"
        for p in places:
            prompt += f"- {p['name']} (Rating: {p.get('rating', 'N/A')})\n"

        # Call OpenAI API to get ranking
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
            # Clean and normalize the extracted name
            cleaned_name = normalize(match.group(1))
            if not cleaned_name:
                continue

            # Find the best matching place from our list
            # Find the best matching place from our list
            close_matches = difflib.get_close_matches(cleaned_name, normalized_places.keys(), n=1, cutoff=0.7)

            # If we found a match, add it to our ranked places
            # If we found a match, add it to our ranked places
            if close_matches:
                best_match = close_matches[0]
                place = normalized_places[best_match]
                if place["name"] not in matched_names:
                    matched_names.add(place["name"])
                    ranked_places.append(place)

            # Stop after getting 5 places
            # Stop after getting 5 places
            if len(ranked_places) >= 5:
                break
        
        # If no matches were found, return the top 5 raw results
        # If no matches were found, return the top 5 raw results
        if not ranked_places:
            logger.warning(f"No matches found via AI for {category}. Using top 5 raw results.")
            return places[:5]
        
        return ranked_places