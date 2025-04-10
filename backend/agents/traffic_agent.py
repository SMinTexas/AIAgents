import requests
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TrafficAgent:
    def __init__(self):
        """ Initialize Google Maps API """
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    def get_traffic(self, origin, destination, waypoints, departure_time, stop_durations=None):
        """ 
        Fetch real-time traffic data from Google Maps API 
        """
        estimated_times = []
        traffic_incidents = []
        congestion_levels = []

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

            # Get route details including traffic information
            route_info = self._get_route_details(start, end, departure_dt)
            if not route_info:
                logger.warning(f"Could not get route details for segment {start} to {end}")
                continue

            # Extract traffic information
            traffic_info = self._extract_traffic_info(route_info)

            # Get travel time and congestion level
            travel_time, congestion_level = self._get_travel_time_and_congestion(route_info)

            # Get traffic incidents
            incidents = self._get_traffic_incidents(start, end)
            if incidents:
                traffic_incidents.extend(incidents)

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

            # Add segment information
            segment_info = {
                "stop": end,
                "arrival_date_time": formatted_arrival_datetime,
                "travel_time": f"{int(travel_time // 60)} hours {int(travel_time % 60)} minutes",
                "stop_duration": (f"{stop_duration // 60} hours" if stop_duration % 60 == 0 else f"{stop_duration // 60} hours{stop_duration % 60} minutes") if stop_duration else "Final destination",
                "coords": lat_lng,
                "congestion_level": congestion_level,
                "traffic_incidents": incidents,
                "alternative_routes": traffic_info.get("alternatives", []),
                "traffic_delay": traffic_info.get("delay", 0)
            }

            estimated_times.append(segment_info)
            congestion_levels.append(congestion_level)

        return {"estimated_stops": estimated_times}
    
    def _get_route_details(self, origin, destination, departure_time):
        """
        Get detailed route information including traffic data
        """
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": int(departure_time.timestamp()),
            "key": self.api_key,
            "alternatives": "true" # Get alternative routes
        }

        try:
            response = requests.get(url, params=params).json()
            if response["status"] == "OK":
                return response
            logger.warning(f"Route API returned status: {response['status']}")
            return None
        except Exception as e:
            logger.error(f"Error fetching route details: {str(e)}")
            return None
        
    def _extract_traffic_info(self, route_info):
        """
        Extract traffic-related information from route details
        """
        traffic_info = {
            "delay": 0,
            "alternatives": []
        }

        if not route_info or "routes" not in route_info:
            return traffic_info
        
        # Get the main route
        main_route = route_info["routes"][0]

        # Calculate delay based on duration_in_traffic vs duration
        if "legs" in main_route:
            for leg in main_route["legs"]:
                if "duration_in_traffic" in leg and "duration" in leg:
                    traffic_info["delay"] = leg["duration_in_traffic"]["value"] - leg["duration"]["value"]

        # Get alternative routes
        if len(route_info["routes"]) > 1:
            for alt_route in route_info["routes"][1:]:
                if "legs" in alt_route:
                    alt_info = {
                        "duration": alt_route["legs"][0]["duration"]["text"],
                        "distance": alt_route["legs"][0]["distance"]["text"],
                        "summary": alt_route["summary"]
                    }
                    traffic_info["alternatives"].append(alt_info)

        return traffic_info
    
    def _get_travel_time_and_congestion(self, route_info):
        """
        Calculate travel time and congestion level from route info
        """
        if not route_info or "routes" not in route_info:
            return 0, "unknown"
        
        route = route_info["routes"][0]
        if "legs" not in route:
            return 0, "unknown"
        
        leg = route["legs"][0]

        # Get travel time
        if "duration_in_traffic" in leg:
            travel_time = leg["duration_in_traffic"]["value"] / 60 # Covert to minutes
        elif "duration" in leg:
            travel_time = leg["duration"]["value"] / 60
        else:
            travel_time = 0

        # Calculate congestion level
        if "duration_in_traffic" in leg and "duration" in leg:
            delay_ratio = leg["duration_in_traffic"]["value"] / leg["duration"]["value"]
            if delay_ratio > 1.5:
                congestion_level = "heavy"
            elif delay_ratio > 1.2:
                congestion_level = "moderate"
            else:
                congestion_level = "light"
        else:
            congestion_level = "unknown"

        return travel_time, congestion_level
    
    def _get_traffic_incidents(self, origin, destination):
        """
        Get traffic incidents between origin and destination
        """
        # Note:  this is a placeholder.  Google Maps does not directly provide incident data
        # I will need to locate a different API to provide this info
        return []
    
    def _calculate_overall_congestion(self, congestion_levels):
        """
        Calculate overall congestion level for the entire route
        """
        if not congestion_levels:
            return "Unknown"
        
        heavy_count = congestion_levels.count("heavy")
        moderate_count = congestion_levels.count("moderate")

        if heavy_count > len(congestion_levels) / 2:
            return "heavy"
        elif moderate_count + heavy_count > len(congestion_levels) / 2:
            return "moderate"
        else:
            return "light"
        
    def _get_lat_lng(self, address):
        """ 
        Geocode address into latitude and longitude using Google Geocoding API 
        """
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