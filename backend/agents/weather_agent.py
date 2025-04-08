# import requests
import httpx
import os
# from requests.utils import quote # Ensure encoding works
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class WeatherAgent:
    def __init__(self):
        """ Initialize WeatherAPI """
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("WeatherAPI key not found!  Check your .env file.")
        self.base_url = "http://api.weatherapi.com/v1/current.json"

        # Create an async client with explicit proxy settings
        self.http_client = httpx.AsyncClient(
            verify=False,
            proxies=None,
            timeout=30.0
        )

        logger.info("WeatherAgent initialized with API key: %s", self.api_key[:4] + "..." if self.api_key else "None")

    async def get_weather(self, route_info):
        """ Fetch weather data for a given location using WeatherAPI 
        :param location: City name (e.g. "Katy") or coordinates ("lat,lon")
        :return Weather details as JSON
        """
        weather_data = {}

        if not route_info or "waypoints" not in route_info:
            logger.error(f"No waypoints provided for weather lookup")
            return {"error": "No waypoints provided for weather lookup"}

        stops = route_info.get("waypoints", [])
        logger.info(f"Processing weather for stops: {stops}")

        # Add the destination as a final stop (grabbed from the last leg)
        if "legs" in route_info:
            legs = route_info["legs"]
            if isinstance(legs, list) and len(legs) > 0:
                # Add origin from first leg
                first_leg = legs[0]
                if isinstance(first_leg, dict) and "start_location" in first_leg:
                    origin = first_leg["start_location"]
                    if origin not in stops:
                        stops.insert(0, origin)
                        logger.info(f"Added origin to stops: {origin}")

                # Add destination from last leg
                last_leg = legs[-1]
                if isinstance(last_leg, dict) and "end_location" in last_leg:
                    destination = last_leg["end_location"]
                    if destination not in stops:
                        stops.append(destination)
                        logger.info(f"Added destination to stops: {destination}")

        # Ensure we have at least one stop to process
        if not stops:
            logger.error("No stops provided for weather lookup")
            return {"error": "No stops provided for weather lookup"}
        
        for waypoint in stops:
            try:
                encoded_waypoint = quote(waypoint)  # Encode correctly
                url = f"{self.base_url}?key={self.api_key}&q={encoded_waypoint}&aqi=no"
                logger.info(f"Fetching weather for {waypoint} using URL: {url}")
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