import os
import googlemaps
import folium
import polyline
import datetime


class TravelAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key not found.  This should have been caught during startup.")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.locations = {}

    def get_route(self, origin, destination, waypoints=[]):
        """ Fetch optimized route and return travel time in hours and minutes. """
        try:   
            # Build the request parameters
            params = {
                "origin": origin,
                "destination": destination,
                "waypoints": waypoints,
                "mode": "driving",
                "departure_time": "now"
            }

            # Call Google Directions API
            route_result = self.gmaps.directions(**params)

            if not route_result:
                print(f"No routes found.")
                return {"error": "No route data available."}

            # Initialize total values
            total_distance_meters = 0
            total_duration_seconds = 0  
            all_legs = []

            # Extract waypoints from the response
            extracted_waypoints = []

            for i, leg in enumerate(route_result[0]['legs']):
                total_distance_meters += leg['distance']['value']
                total_duration_seconds += leg['duration']['value']

                # Store individual leg details
                all_legs.append({
                    "start_address": leg['start_address'],
                    "end_address": leg['end_address'],
                    "distance_text": leg['distance']['text'],
                    "duration_text": leg['duration']['text']
                })

                # Add intermediate stops (excluding origin and destination)
                # if i > 0 and i < len(route_result[0]['legs']) - 1:
                #     extracted_waypoints.append(leg['start_address'])
                if i < len(route_result[0]['legs']) - 1:
                    extracted_waypoints.append(leg['end_address'])
                    
            # Convert total distance and duration
            total_distance_miles = total_distance_meters * 0.000621371
            total_duration_hours = total_duration_seconds / 3600
            total_duration_text = f"{int(total_duration_seconds // 3600)} hours {int((total_duration_seconds % 3600) // 60)} minutes"

            return {
                "total_distance_miles": round(total_distance_miles, 2),
                "total_distance_text": f"{round(total_distance_miles, 2)} miles",
                "estimated_time_hours": round(total_duration_hours, 2),
                "estimated_time_text": total_duration_text,
                "polyline": route_result[0]['overview_polyline']['points'],
                "legs": all_legs,
                "waypoints": extracted_waypoints
            }
        
        except Exception as e:
            return {"error": "An error occurred while fetching the route."}
    
    def get_real_time_traffic(self, origin, destination, waypoints=[]):
        """ Get real-time traffic duration in hours and minutes. """
        try:
            # Build the request parameters
            params = {
                "origin": origin,
                "destination": destination,
                "waypoints": waypoints,
                "mode": "driving",
                "departure_time": "now"
            }

            # Call Google Directions API
            route_result = self.gmaps.directions(**params)
            
            if not route_result:
                print(f"No routes found.")
                return {"error": "No route data available."}
            
            total_duration_seconds = sum(
                leg.get("duration_in_traffic", leg["duration"])["value"]
                for leg in route_result[0]["legs"]
            )

            total_duration_hours = total_duration_seconds / 3600
            hours = total_duration_seconds // 3600
            minutes = (total_duration_seconds % 3600) // 60 
            total_duration_text = f"{int(hours)} hours {int(minutes)} minutes"

            # Calculate traffic status dynamically
            traffic_status = self.get_traffic_condition(total_duration_seconds)

            return {
                "total_duration_hours": round(total_duration_hours, 2),
                "total_duration_text": total_duration_text,
                "traffic_status": traffic_status
            }
        
        except Exception as e:
            return {"error": "An error occurred while fetching real-time traffic conditions."}
    
    def get_traffic_condition(self, total_seconds):
        """ Determine traffic status based on duration increase. """
        if total_seconds < 1800: # Less than 30 minutes
            return "Light"
        elif total_seconds < 3600: # 30 minutes to 1 hour
            return "Moderate"
        elif total_seconds < 7200: # 1 to 2 hours
            return "Heavy"
        else:
            return "Severe"