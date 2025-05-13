import os
import googlemaps
import folium
import polyline
import datetime

class TravelAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        print(f"\nInitializing TravelAgent")
        print(f"API Key present: {bool(self.api_key)}")
        print(f"API Key length: {len(self.api_key) if self.api_key else 0}")
        print(f"API Key first 10 chars: {self.api_key[:10] if self.api_key else 'None'}")
        
        if not self.api_key:
            raise ValueError("Google Maps API key not found. This should have been caught during startup.")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.locations = {}

    def get_route(self, origin, destination, waypoints=[]):
        """ Fetch optimized route and return travel time in hours and minutes. """
        try:   
            print(f"\nFetching route from {origin} to {destination}")
            print(f"Waypoints: {waypoints}")
            
            # Build the request parameters
            params = {
                "origin": origin,
                "destination": destination,
                "mode": "driving",
                "departure_time": "now"
            }
            
            # Only add waypoints if they exist
            if waypoints and len(waypoints) > 0:
                params["waypoints"] = waypoints
                print(f"Added waypoints to request: {waypoints}")

            print(f"Google Maps API request params: {params}")

            try:
                # Call Google Directions API
                route_result = self.gmaps.directions(**params)
            except Exception as api_error:
                print(f"Google Maps API Error: {str(api_error)}")
                print(f"Error type: {type(api_error)}")
                if hasattr(api_error, 'response'):
                    print(f"API Response: {api_error.response}")
                return {"error": f"Google Maps API Error: {str(api_error)}"}

            if not route_result:
                print(f"No routes found for {origin} to {destination}")
                return {"error": "No route data available."}

            print(f"Route result received: {len(route_result)} routes found")

            # Initialize total values
            total_distance_meters = 0
            total_duration_seconds = 0  
            all_legs = []

            # Extract waypoints from the response
            extracted_waypoints = []

            try:
                for i, leg in enumerate(route_result[0]['legs']):
                    total_distance_meters += leg['distance']['value']
                    total_duration_seconds += leg['duration']['value']

                    # Store individual leg details
                    all_legs.append({
                        "start_address": leg['start_address'],
                        "end_address": leg['end_address'],
                        "distance_text": leg['distance']['text'],
                        "duration_text": leg['duration']['text'],
                        "end_location": leg.get('end_location', {})
                    })

                    # Add intermediate stops (excluding origin and destination)
                    if i < len(route_result[0]['legs']) - 1:
                        extracted_waypoints.append(leg['end_address'])
                        
                # Convert total distance and duration
                total_distance_miles = total_distance_meters * 0.000621371
                total_duration_hours = total_duration_seconds / 3600
                total_duration_text = f"{int(total_duration_seconds // 3600)} hours {int((total_duration_seconds % 3600) // 60)} minutes"

                # Get the polyline for the route
                polyline_points = route_result[0]['overview_polyline']['points']
                
                # Get the destination coordinates
                destination_coords = None
                if route_result[0]['legs'] and len(route_result[0]['legs']) > 0:
                    last_leg = route_result[0]['legs'][-1]
                    if 'end_location' in last_leg:
                        destination_coords = [last_leg['end_location']['lat'], last_leg['end_location']['lng']]

                print(f"Route processed successfully:")
                print(f"- Total distance: {total_distance_miles:.2f} miles")
                print(f"- Total duration: {total_duration_hours:.2f} hours")
                print(f"- Number of waypoints: {len(extracted_waypoints)}")
                print(f"- Has polyline: {bool(polyline_points)}")
                print(f"- Has destination coords: {bool(destination_coords)}")

                return {
                    "total_distance_miles": round(total_distance_miles, 2),
                    "total_distance_text": f"{round(total_distance_miles, 2)} miles",
                    "estimated_time_hours": round(total_duration_hours, 2),
                    "estimated_time_text": total_duration_text,
                    "polyline": polyline_points,
                    "legs": all_legs,
                    "waypoints": extracted_waypoints,
                    "destination_coords": destination_coords
                }
            except KeyError as e:
                print(f"Error processing route data: {str(e)}")
                print(f"Route result structure: {route_result}")
                return {"error": f"Error processing route data: {str(e)}"}
        
        except Exception as e:
            print(f"Error in get_route: {str(e)}")
            print(f"Request parameters: origin={origin}, destination={destination}, waypoints={waypoints}")
            return {"error": f"An error occurred while fetching the route: {str(e)}"}
    
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
            total_duration_text = f"{int(total_duration_seconds // 3600)} hours {int((total_duration_seconds % 3600) // 60)} minutes"
            
            return {
                "total_duration_hours": round(total_duration_hours, 2),
                "total_duration_text": total_duration_text
            }
        
        except Exception as e:
            return {"error": "An error occurred while fetching traffic data."}
    
    def get_traffic_condition(self, total_seconds):
        """ Determine traffic condition based on duration. """
        if total_seconds < 3600:  # Less than 1 hour
            return "Light"
        elif total_seconds < 7200:  # Less than 2 hours
            return "Moderate"
        else:
            return "Heavy"