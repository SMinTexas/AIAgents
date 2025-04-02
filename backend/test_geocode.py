import googlemaps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=api_key)

# Test locations
locations = ["Katy, TX", "Orlando, FL", "New Orleans, LA", "Pensacola, FL"]

for loc in locations:
    try:
        result = gmaps.geocode(loc)
        if result:
            print(f"\n Found location: {loc}")
            print(f" Address: {result[0]['formatted_address']}")
            print(f" Coordinates: {result[0]['geometry']['location']}")
        else:
            print(f"\n Location not found: {loc}")
    except Exception as e:
        print(f"\n Error fetching location {loc}: {str(e)}")