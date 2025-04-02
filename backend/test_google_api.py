import googlemaps
import os
from dotenv import load_dotenv

# Load envirnoment variables
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize the Google Maps Client
gmaps = googlemaps.Client(key=api_key)

# Test Inputs
origin = "Katy, TX"
destination = "Orlando, FL"
waypoints = ["New Orleans, LA", "Pensacola, FL"]

try:
    route_result = gmaps.directions(
        origin, 
        destination, 
        waypoints=waypoints, 
        mode="driving", 
        departure_time="now"
    )

    print("\n Google Maps API Response:")
    print(route_result)

except Exception as e:
    print(f"\n Error: (e)")