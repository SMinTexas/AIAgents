import requests
import os
from datetime import datetime, timedelta

class TrafficAgent:
    def __init__(self):
        """ Initialize Google Maps API """
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    def get_traffic(self, origin, destination, waypoints, departure_time, stop_durations=None):
        """ Fetch real-time traffic data from Google Maps API """
        estimated_times = []
        # total_time_minutes = 0

        departure_dt = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")

        stops = [origin] + waypoints + [destination]

        # Ensure stop durations match waypoints, with a default of 30 minutes per stop
        if not stop_durations:
            stop_durations = [0] * len(waypoints)
        else:
            stop_durations = [int(d) * 60 for d in stop_durations] # Convert from hours to minutes

        # Iterate through each segment of the trip
        for i in range(len(stops) - 1):
            start = stops[i]
            end = stops[i + 1]

            params = {
                "origins": start,
                "destinations": end,
                "key": self.api_key,
                "departure_time": int(departure_dt.timestamp())  
            }

            response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params).json()

            try:
                elements = response["rows"][0]["elements"][0]

                # Extract travel time in minutes
                if "duration_in_traffic" in elements:
                    travel_time = elements["duration_in_traffic"]["value"] / 60  # Convert to minutes
                elif "duration" in elements:
                    travel_time = elements["duration"]["value"] / 60 # Use normal duration
                else:
                    travel_time = 0 # Default if no valid data

            except (KeyError, IndexError):
                travel_time = 0

            # Calculate estimated arrival time (travel time only)
            arrival_time = departure_dt + timedelta(minutes=travel_time)
            formatted_arrival_datetime = arrival_time.strftime("%Y-%m-%d %I:%M %p")

            # Ensure stop duration is correctly indexed
            stop_duration = stop_durations[i] if i < len(stop_durations) else 0

            # Compute the new departure time (arrival time + stop duration)
            departure_dt = arrival_time + timedelta(minutes=stop_duration)
            formatted_departure_datetime = departure_dt.strftime("%Y-%m-%d %I:%M %p")

            # Fetch Lat/Lng for Traffic Stop
            lat_lng = self._get_lat_lng(end)

            estimated_times.append({
                "stop": end,
                "arrival_date_time": formatted_arrival_datetime,
                "travel_time": f"{int(travel_time // 60)} hours {int(travel_time % 60)} minutes",
                "stop_duration": (f"{stop_duration // 60} hours" if stop_duration % 60 == 0 else f"{stop_duration // 60} hours{stop_duration % 60} minutes") if stop_duration else "Final destination",
                "coords": lat_lng
            })

        return {"estimated_stops": estimated_times}
    
    def _get_lat_lng(self, address):
        """ Geocode address into latitude and longitude using Google Geocoding API """
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }

        response = requests.get(geocode_url, params=params).json()

        if "results" in response and response["results"]:
            location = response["results"][0]["geometry"]["location"]
            return [location['lat'], location['lng']]
        return None