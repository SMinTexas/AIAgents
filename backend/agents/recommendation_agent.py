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

from utils import cache_manager
import logging

# Set up logging with a more concise format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Valid Google Places API types
VALID_PLACE_TYPES = {
    'museum': 'museum',
    'restaurant': 'restaurant',
    'shopping_mall': 'shopping_mall',
    'zoo': 'zoo',
    'casino': 'casino',
    'aquarium': 'aquarium',
    'amusement_park': 'amusement_park',
    'art_gallery': 'art_gallery',
    'bowling_alley': 'bowling_alley',
    'movie_theater': 'movie_theater',
    'night_club': 'night_club',
    'park': 'park',
    'stadium': 'stadium',
    'tourist_attraction': 'tourist_attraction',
    'hotels': 'lodging',
    'logding': 'lodging'
}

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

def normalize(name):
    return re.sub(r"[^\w\s]", "", name).lower().strip()

class RecommendationAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key not found")
        logger.info(f"Initializing RecommendationAgent with API key: {self.api_key[:8]}...")
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.http_client = httpx.AsyncClient()

    def _process_places_results(self, results, max_results=5):
        """Helper method to process and sort places results"""
        if not results or 'results' not in results:
            return []
        
        # Sort by rating if available
        sorted_places = sorted(
            results['results'],
            key=lambda x: x.get('rating', 0),
            reverse=True
        )
        return sorted_places[:max_results]

    async def get_recommendations(self, locations, preferences):
        """Get recommendations for each location based on preferences"""
        logger.info(f"Getting recommendations for locations: {locations}")
        logger.info(f"With preferences: {preferences}")
        
        recommendations = {}
        
        # Skip the first location (origin) and process the rest
        for location in locations[1:]: # Start from index 1 to skip origin
            logger.info(f"Processing location: {location}")
            try:
                # Get coordinates for the location
                logger.info(f"Geocoding location: {location}")
                geocode_result = await asyncio.to_thread(self.gmaps.geocode, location)
                if not geocode_result:
                    logger.warning(f"Could not geocode location: {location}")
                    continue
                
                location_data = geocode_result[0]
                lat = location_data['geometry']['location']['lat']
                lng = location_data['geometry']['location']['lng']
                
                logger.info(f"Coordinates for {location}: {lat}, {lng}")
                
                # Initialize recommendations for this location
                recommendations[location] = {
                    "hotels": [],
                    "restaurants": [],
                    "attractions": []
                }
                
                # Always get hotels
                try:
                    logger.info(f"Getting hotels for {location} at coordinates ({lat}, {lng})")
                    hotels = await asyncio.to_thread(
                        self.gmaps.places_nearby,
                        location=(lat, lng),
                        type='lodging',
                        radius=5000
                    )

                    recommendations[location]["hotels"] = self._process_places_results(hotels)
                    logger.info(f"Found {len(recommendations[location]['hotels'])} hotels")
                except Exception as e:
                    logger.error(f"Error getting hotels for {location}: {str(e)}")
                    logger.error(f"Error type: {type(e)}")
                    if hasattr(e, 'response'):
                        logger.error(f"Response status: {e.response.status_code}")
                        logger.error(f"Response body: {e.response.text}")
                
                # Always get restaurants
                try:
                    logger.info(f"Getting restaurants for {location} at coordinates ({lat}, {lng})")
                    restaurants = await asyncio.to_thread(
                        self.gmaps.places_nearby,
                        location=(lat, lng),
                        type='restaurant',
                        radius=5000  # 5km radius
                    )
                    
                    recommendations[location]["restaurants"] = self._process_places_results(restaurants)
                    logger.info(f"Found {len(recommendations[location]['restaurants'])} restaurants")
                except Exception as e:
                    logger.error(f"Error getting restaurants for {location}: {str(e)}")
                    logger.error(f"Error type: {type(e)}")
                    if hasattr(e, 'response'):
                        logger.error(f"Response status: {e.response.status_code}")
                        logger.error(f"Response body: {e.response.text}")
                
                # Get attractions based on preferences
                for preference in preferences:
                    logger.info(f"preference: {preference}")
                    if preference not in VALID_PLACE_TYPES:
                        logger.warning(f"Invalid place type: {preference}")
                        continue
                        
                    try:
                        logger.info(f"Getting {preference} for {location} at coordinates ({lat}, {lng})")
                        places = await asyncio.to_thread(
                            self.gmaps.places_nearby,
                            location=(lat, lng),
                            type=VALID_PLACE_TYPES[preference],
                            radius=5000  # 5km radius
                        )
                        
                        attractions = self._process_places_results(places, max_results=3) # Limit to 3 per type
                        recommendations[location]["attractions"].extend(attractions)
                        logger.info(f"Found {len(attractions)} {preference}")
                    except Exception as e:
                        logger.error(f"Error getting {preference} for {location}: {str(e)}")
                        logger.error(f"Error type: {type(e)}")
                        if hasattr(e, 'response'):
                            logger.error(f"Response status: {e.response.status_code}")
                            logger.error(f"Response body: {e.response.text}")
                
                # Limit total attractions per location to prevent too many markers
                            if len(recommendations[location]["attractions"]) > 9:
                                # Sort by rating and take the top 9
                                recommendations[location]["attractions"].sort(key=lambda x: x.get('rating', 0), reverse=True)
                                recommendations[location]["attractions"] = recommendations[location]["attractions"][:9]
                                logger.info(f"Limited attractions for {location} to top 9 by rating")

            except Exception as e:
                logger.error(f"Error processing location {location}: {str(e)}")
                logger.error(f"Error type: {type(e)}")
                if hasattr(e, 'response'):
                    logger.error(f"Response status: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                continue
        
        logger.info(f"Final recommendations structure: {recommendations}")
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
            logger.warning(f"No matches found via AI for {category}. Using top 5 raw results.")
            return places[:5]
        
        return ranked_places

    async def get_route_attractions(self, route_coordinates, preferences, max_distance=5000, max_attractions_per_type=3, max_total_attractions=15):
        """
        Find attractions along the route, not just at waypoints
        :param route_coordinates: List of [lat, lng] coordinates along the route
        :param preferences: List of place types to search for
        :param max_distance: Maximum distance in meters from route to search for attractions
        :param max_attractions_per_type: Maximum number of attractions per type to return
        :param max_total_attractions: Maximum total number of attractions to return
        :return: Dictionary of attractions found along the route
        """
        logger.info(f"Searching for attractions along route with {len(route_coordinates)} points")
        
        # Skip the first 10% of coordinates to avoid searching near origin
        start_index = int(len(route_coordinates) * 0.1)
        route_coordinates = route_coordinates[start_index:]

        # Sample points along the route (every 10th point to avoid too many API calls)
        sampled_points = route_coordinates[::10]
        logger.info(f"Sampling {len(sampled_points)} points along route")
        
        # route_attractions = []
        # Track attractions by type of limit per type
        attractions_by_type = {}
        
        for point in sampled_points:
            lat, lng = point
            
            # Search for each preferred attraction type
            for preference in preferences:
                if preference not in VALID_PLACE_TYPES:
                    logger.warning(f"Invalid place type: {preference}")
                    continue
                    
                # Skip if we already have enough of this type
                if preference in attractions_by_type and len(attractions_by_type[preference]) >= max_attractions_per_type:
                    continue

                try:
                    logger.info(f"Searching for {preference} near coordinates ({lat}, {lng})")
                    places = self.gmaps.places_nearby(
                        location=(lat, lng),
                        type=VALID_PLACE_TYPES[preference],
                        radius=max_distance
                    )
                    
                    if places and 'results' in places:
                        # Initialize list for this type if not exists
                        if preference not in attractions_by_type:
                            attractions_by_type[preference] = []

                        for place in places['results']:
                            # Stop if we have enough of this type
                            if len(attractions_by_type[preference]) >= max_attractions_per_type:
                                   break

                            # Calculate distance from route point
                            place_location = place['geometry']['location']
                            distance = self._calculate_distance(
                                (lat, lng),
                                (place_location['lat'], place_location['lng'])
                            )
                            
                            # Only include if within max_distance
                            if distance <= max_distance:
                                attraction = {
                                    'name': place['name'],
                                    'type': preference,
                                    'location': place_location,
                                    'rating': place.get('rating', 0),
                                    'distance_from_route': distance,
                                    'place_id': place.get('place_id')
                                }
                                # route_attractions.append(attraction)
                                attractions_by_type[preference].append(attraction)
                                
                except Exception as e:
                    logger.error(f"Error searching for {preference} near ({lat}, {lng}): {str(e)}")
                    continue
        
        # Combine all attractions and sort by rating and distance
        route_attractions = []
        for preference, attractions in attractions_by_type.items():
            # Sort attractions for this type by rating and distance
            attractions.sort(key=lambda x: (x['rating'], -x['distance_from_route']), reverse=True)
            route_attractions.extend(attractions)
        
        # Sort attractions by rating and distance
        route_attractions.sort(key=lambda x: (x['rating'], -x['distance_from_route']), reverse=True)

        # Remove duplicates (same place_id)
        seen_place_ids = set()
        unique_attractions = []
        for attraction in route_attractions:
            if attraction['place_id'] not in seen_place_ids:
                seen_place_ids.add(attraction['place_id'])
                unique_attractions.append(attraction)
        
                # Stop if we have reached the total limit
                if len(unique_attractions) >= max_total_attractions:
                    break;
        
        logger.info(f"Found {len(unique_attractions)} unique attractions along route")
        return unique_attractions

    def _calculate_distance(self, point1, point2):
        """
        Calculate distance between two points using Haversine formula
        :param point1: Tuple of (lat, lng)
        :param point2: Tuple of (lat, lng)
        :return: Distance in meters
        """
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lng1 = point1
        lat2, lng2 = point2
        
        R = 6371000  # Earth's radius in meters
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance