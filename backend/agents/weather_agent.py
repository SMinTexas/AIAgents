import requests
import os
from requests.utils import quote # Ensure encoding works

class WeatherAgent:
    def __init__(self):
        """ Initialize OpenWeatherMap API """
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not found!  Check your .env file.")
        self.base_url = "http://api.weatherapi.com/v1/current.json"

    def get_weather(self, route_info):
        """ Fetch weather data for a given location using WeatherAPI 
        :param location: City name (e.g. "Katy") or coordinates ("lat,lon")
        :return Weather details as JSON
        """
        weather_data = {}

        if not route_info or "waypoints" not in route_info:
            return {"error": "No waypoints provided for weather lookup"}

        stops = route_info.get("waypoints",[])

        # Add the destination as a final stop (grabbed from the last leg)
        if "legs" in route_info and route_info["legs"]:
            destination = route_info["legs"][-1]["end_address"]
            stops.append(destination)

        
        for waypoint in stops:
            try:
                encoded_waypoint = quote(waypoint)  # Encode correctly
                url = f"{self.base_url}?key={self.api_key}&q={encoded_waypoint}&aqi=no"

                response = requests.get(url)

                response.raise_for_status()
                data = response.json()

                if "error" in data:
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
                    print(data["location"])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching weather data for {waypoint}: {str(e)}")
                return None
            
        return weather_data
        

    
