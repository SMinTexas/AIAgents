import httpx
import os
from urllib.parse import quote
import logging
import googlemaps

logger = logging.getLogger(__name__)

class WeatherAgent:
    def __init__(self):
        """ Initialize WeatherAPI """
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key or not self.google_api_key:
            raise ValueError("API keys not found! Check your .env file.")
        self.base_url = "http://api.weatherapi.com/v1/current.json"
        
        # Create an async client with explicit proxy settings
        self.http_client = httpx.AsyncClient(
            verify=False,
            proxies=None,
            timeout=30.0
        )
        
        # Initialize Google Maps client
        self.gmaps = googlemaps.Client(key=self.google_api_key)
        
        logger.info("WeatherAgent initialized with API keys")

    async def _get_lat_lng(self, address):
        """ Get latitude and longitude for an address using Google Maps API """
        try:
            # Add state/country to the address if not present
            if "katy" in address.lower() and "texas" not in address.lower():
                address = f"{address}, Texas, USA"
            
            print(f"Geocoding address: {address}")
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                formatted_address = geocode_result[0]['formatted_address']
                print(f"Geocoding result for {address}:")
                print(f"- Formatted address: {formatted_address}")
                print(f"- Location: {location}")
                return f"{location['lat']},{location['lng']}"
            return None
        except Exception as e:
            logger.error(f"Error getting lat/lng for {address}: {str(e)}")
            return None

    async def get_weather(self, route_info):
        """ Fetch weather data for a given location using WeatherAPI 
        :param location: City name (e.g. "Katy") or coordinates ("lat,lon")
        :return Weather details as JSON
        """
        weather_data = {}

        if not route_info or "waypoints" not in route_info:
            logger.error("No waypoints provided for weather lookup")
            return {"error": "No waypoints provided for weather lookup"}

        stops = route_info.get("waypoints", [])
        logger.info(f"Processing weather for stops: {stops}")

        # Add both origin and destination if they're not already included
        if "legs" in route_info:
            legs = route_info["legs"]
            if isinstance(legs, list) and len(legs) > 0:
                # Add origin from first leg
                first_leg = legs[0]
                if isinstance(first_leg, dict) and "start_address" in first_leg:
                    origin = first_leg["start_address"]
                    if origin not in stops:
                        stops.insert(0, origin)
                        logger.info(f"Added origin to stops: {origin}")

                # Add destination from last leg
                last_leg = legs[-1]
                if isinstance(last_leg, dict) and "end_address" in last_leg:
                    destination = last_leg["end_address"]
                    if destination not in stops:
                        stops.append(destination)
                        logger.info(f"Added destination to stops: {destination}")

        # Ensure we have at least one stop to process
        if not stops:
            logger.error("No stops provided for weather lookup")
            return {"error": "No stops provided for weather lookup"}

        for waypoint in stops:
            try:
                # First get the coordinates using Google Maps
                coords = await self._get_lat_lng(waypoint)
                if not coords:
                    logger.error(f"Could not get coordinates for {waypoint}")
                    weather_data[waypoint] = {"error": "Could not get coordinates"}
                    continue

                # Use the coordinates to get weather data
                url = f"{self.base_url}?key={self.api_key}&q={coords}&aqi=no"
                
                logger.info(f"Fetching weather for {waypoint} using coordinates: {coords}")
                response = await self.http_client.get(url)
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    logger.error(f"Weather API error for {waypoint}: {data['error']['message']}")
                    weather_data[waypoint] = {"error": data["error"]["message"]}
                else:
                    weather_data[waypoint] = {
                        "location": data["location"]["name"],
                        "region": data["location"]["region"],
                        "country": data["location"]["country"],
                        "temperature": f"{data['current']['temp_f']}°F",
                        "temperature_c": f"{data['current']['temp_c']}°C",
                        "condition": data["current"]["condition"]["text"],
                        "humidity": f"{data['current']['humidity']}%",
                        "wind_speed_mph": f"{data['current']['wind_mph']} mph",
                        "wind_speed_kph": f"{data['current']['wind_kph']} kph",
                        "coords": {
                            "lat": data["location"]["lat"], 
                            "lng": data["location"]["lon"]
                        }
                    }
                    logger.info(f"Successfully fetched weather for {waypoint}: {weather_data[waypoint]['temperature']} and {weather_data[waypoint]['condition']}")
                    logger.debug(f"Full weather data for {waypoint}: {weather_data[waypoint]}")
            except httpx.RequestError as e:
                logger.error(f"Error fetching weather data for {waypoint}: {str(e)}")
                weather_data[waypoint] = {"error": str(e)}
            except Exception as e:
                logger.error(f"Unexpected error fetching weather data for {waypoint}: {str(e)}")
                weather_data[waypoint] = {"error": str(e)}

        logger.info(f"Completed weather lookup for {len(weather_data)} locations")
        logger.info(f"Locations with weather data: {list(weather_data.keys())}")
        return weather_data
        

    
