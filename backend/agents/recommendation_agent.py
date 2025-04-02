import requests
import os
import time
import openai
import re
import aiohttp
import asyncio
from difflib import SequenceMatcher
import difflib

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

def normalize(name):
    return re.sub(r"[^\w\s]", "", name).lower().strip()

class RecommendationAgent:
    def __init__(self):
        """ Initialize Google Places API """
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.geocode_cache = {}
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2025-01-01-preview"
        )
        self.attraction_types=["museum","tourist_attraction","shopping_mall","zoo","casino","aquarium"]
        self.base_places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    # async def get_recommendations(self, locations, food_preference="Any", lodging_preference="Hotel", attraction_preference=None):
    async def get_recommendations(self, location):
        """ Fetch recommendations for restaurants, hotels, and attractions """
        # if attraction_preference is None:
        #     attraction_preference = ["museum"]
        recommendations = {}

        for loc in location:
            lat_lng = await self._get_lat_lng(loc)
            if not lat_lng:
                continue

            restaurants = await self._fetch_places(lat_lng, "restaurant")
            print(f"\n[DEBUG] Raw restaurants for {loc}: {[r['name'] for r in restaurants]}")
            hotels = await self._fetch_places(lat_lng, "lodging")
            # attractions = self._fetch_places(lat_lng, "museum", attraction_preference)
            # Get attractions across multiple categories, limit the total to 5
            all_attractions = []
            for attr_type in self.attraction_types:
                # if len(attractions) >= 5:
                #     break
                # fetched = await self._fetch_places(location, "attraction", attraction_type)
                # needed = 5 - len(attractions)
                # attractions.extend(fetched[:needed])
                # attractions.extend(
                #     self._fetch_places(lat_lng, attraction_type, attraction_type)
                # )
                places = await self._fetch_places(lat_lng, attr_type)
                all_attractions.extend(places)

            unique_attractions = {p["place_id"]: p for p in all_attractions}.values()
            attractions = list(unique_attractions)[:5]

            # Use OpenAI to refine recommendations
            best_restaurants = self._rank_with_ai(restaurants, "restaurants")
            # print(f"[DEBUG] Best restaurants for {loc}: {[r['name'] for r in best_restaurants]}")
            print(f"[DEBUG] AI-ranked restaurant count for {loc}: {len(best_restaurants)}")
            best_hotels = self._rank_with_ai(hotels, "hotels")
            print(f"[DEBUG] AI-ranked hotel count for {loc}: {len(best_hotels)}")

            # Fetch detailed information for each place
            restaurant_details = await self._get_place_details_async(best_restaurants)
            hotel_details = await self._get_place_details_async(best_hotels)
            attraction_details = await self._get_place_details_async(attractions)

            recommendations[loc] = {
                "restaurants": restaurant_details,
                "hotels": hotel_details,
                "attractions": attraction_details
            }

            print(f"\nFinal recommendations for {loc}:")
            print(f" - Restaurants: {len(restaurant_details)}")
            print(f" - Hotels: {len(hotel_details)}")
            print(f" - Attractions: {len(attraction_details)}")
        return recommendations
    
    def _rank_with_ai(self, places, category):
        """ Use OpenAI to rank places based on user preferences """
        if not places:
            return []
        
        prompt = f"Rank these {category} based on reviews and relevance:\n"
        for p in places:
            prompt += f"- {p['name']} (Rating: {p.get('rating', 'N/A')})\n"

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that ranks restaurants, hotels, and attractions based on user preferences."},
                {"role": "user", "content": prompt}
            ]
        )

        ranked_places = []
        matched_names = set()

        ai_response = response.choices[0].message.content

        # print("\n========================================AI Raw Response=======================================================")
        # print(ai_response)
        # print("================================================================================================================")


        lines = ai_response.split("\n")

        normalized_places = {normalize(p["name"]): p for p in places}

        for line in lines:
            if not re.match(r"^\d+[\.\)]", line.strip()):
                continue

            # match = re.search(r"\d+\.\s*\**(.*?)\**(?:\s*\(|$)", line)
            # match = re.search(r"^\s*[\d•\-]+[.)\s-]*\**(.*?)\**(?:\s*\(|$)", line.strip())
            match = re.search(r"^\s*[\d•\-]+[.)\s-]*\**(.*?)\**(?:\s*\(|$)", line)
            if not match: 
                continue

            cleaned_name = normalize(match.group(1))
            if not cleaned_name:
                continue

            close_matches = difflib.get_close_matches(cleaned_name, normalized_places.keys(), n=1, cutoff=0.7)

            if close_matches:
                best_match = close_matches[0]
                place = normalized_places[best_match]
                if place["name"] not in matched_names:
                    matched_names.add(place["name"])
                    ranked_places.append(place)

            # if match:
            #     cleaned_name = match.group(1).strip().lower()

            #     for place in places:
            #         # place_name_clean = place["name"].strip().lower()

            #         # print(f"Cleaned name: {cleaned_name}")
            #         # print(f"Available names: {[p['name'] for p in places]}")
            #         cleaned_name_norm = normalize(cleaned_name)
            #         place_name_norm = normalize(place["name"])
            #         normalized_place_names = [normalize(p["name"]) for p in places]
            #         print(f"Trying to match AI Cleaned Name {cleaned_name_norm} against places {place_name_norm}")

            #         close_matches = difflib.get_close_matches(cleaned_name_norm, normalized_place_names, n=1, cutoff=0.7)

                    # if close_matches:
                    #     best_match = close_matches[0]
                    #     for place in places:
                    #         if normalize(place["name"]) == best_match and place["name"] not in matched_names:
                    #             matched_names.add(place["name"])
                    #             ranked_places.append(place)
                    #             break

                    # if is_similar(cleaned_name_norm, place_name_norm) and place["name"] not in matched_names:
                    #     matched_names.add(place["name"])
                    #     ranked_places.append(place)
                    #     break

            if len(ranked_places) >= 5:
                break
        
        if not ranked_places:
            print(f"[WARNING] No matches found via AI for {category}.  Using top 5 raw results.")
            return places[:5]
        
        print(f"[DEBUG] Final matched places for {category}: {[p['name'] for p in ranked_places]}")
        return ranked_places
    
    async def _get_lat_lng(self, address):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://maps.googleapis.com/maps/api/geocode/json",params={"address":address,"key":self.google_api_key}) as resp:
                result = await resp.json()
                if result["results"]:
                    loc = result["results"][0]["geometry"]["location"]
                    return f"{loc['lat']},{loc['lng']}"
                
        return None
    
    async def _fetch_places(self, location, place_type):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_places_url, params={
                "location":location,
                "radius": 20000,
                "type":place_type,
                "key":self.google_api_key
            }) as resp:
                result = await resp.json()

                # print(f"\nFetched {place_type} near {location}:")
                # for p in result.get("results", [])[:5]:
                #     print(f" - {p.get('name')} | place_id: {p.get('place_id')} | rating: {p.get('rating')}")

                return [{
                    "name":p["name"],
                    "place_id":p.get("place_id"),
                    "coords":[p["geometry"]["location"]["lat"],p["geometry"]["location"]["lng"]],
                } for p in result.get("results",[]) if p.get("place_id")]

    async def _fetch_detail(self, session, url, place):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        result = data["result"]
                        return {
                            "name": result.get("name", "N/A"),
                            "address": result.get("formatted_address", "N/A"),
                            "phone_number": result.get("formatted_phone_number", "N/A"),
                            "rating": result.get("rating", "N/A"),
                            "opening_hours": result.get("opening_hours", {}).get("weekday_text", "N/A"),
                            "coords": place.get("coords"),
                            "place_id": place["place_id"]
                        }
        except Exception as e:
            print(f"Error fetching details for {place.get('name', 'Unknown')}: {e}")
        return None  
              
    async def _get_place_details_async(self, places):
        results = []
        async with aiohttp.ClientSession() as session:
            for place in places:

                if not place.get("place_id"):
                    print(f"Missing place_id for {place.get('name')}")

                async with session.get(self.details_url, params={
                    "place_id":place["place_id"],
                    "fields":"name,formatted_address,formatted_phone_number,rating,opening_hours",
                    "key":self.google_api_key
                }) as resp:
                    result = await resp.json()
                    if "result" in result:
                        details = result["result"]
                        results.append({
                            "name":details.get("name","N/A"),
                            "address":details.get("formatted_address","N/A"),
                            "phone_number":details.get("formatted_phone_number","N/A"),
                            "rating":details.get("rating","N/A"),
                            "opening_hours":details.get("opening_hours",{}).get("weekday_text",[]),
                            "coords":place.get("coords"),
                            "place_id":place.get("place_id")
                        })

        return results
    
    #LEGACY START
    # def _get_lat_lng(self, address):
    #     """ Geocode address into latitude and longitude using Google Geocoding API """
    #     if address in self.geocode_cache:
    #         return self.geocode_cache[address]
        
    #     geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    #     params = {
    #         "address": address,
    #         "key": self.google_api_key
    #     }

    #     response = requests.get(geocode_url, params=params).json()

    #     if "results" in response and response["results"]:
    #         location = response["results"][0]["geometry"]["location"]
    #         lat_lng = (location['lat'], location['lng'])

    #         self.geocode_cache[address] = lat_lng
    #         return lat_lng
        
    #     return None
        
    # async def _fetch_places(self, location, place_type, preference):
    #     """ Fetches nearby places from Google Places API """
    #     is_attraction = place_type == "attraction"
    #     url = self.base_places_url
    #     params = {
    #         # "location": location, # Ensure this is a lat/lng value
    #         "location": f"{location[0]},{location[1]}",
    #         "radius": 25000,  # 25km radius
    #         # "type": place_type,
    #         "key": self.google_api_key
    #     }

    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url, params=params) as response:
    #             if response.status != 200:
    #                 print(f"Error fetching {place_type} for {location}: HTTP {response.status}")
    #                 return []
                
    #             data = await response.json()

    #             print(f"\nRaw {place_type} results near {location}")
    #             for place in data.get("results", [])[:5]:
    #                 print(f" - {place.get('name')}")

    #             if "results" in data:
    #                 places = [
    #                     {
    #                         "name": place.get("name", "N/A"),
    #                         "place_id": place.get("place_id", ""),
    #                         "coords": [
    #                             place["geometry"]["location"]["lat"],
    #                             place["geometry"]["location"]["lng"]
    #                         ],
    #                         "rating": place.get("rating", "N/A")
    #                     }
    #                     for place in data["results"][:5]
    #                     if "place_id" in place and place["place_id"]
    #                 ]

    #                 print(f"Places fetched for {place_type} near {location}:")
    #                 for p in places:
    #                     print(f" - {p.get('name')} | place_id: {p.get('place_id')} | rating: {p.get('rating')}")

    #                 return places
                
    #             return  []
            

        # if is_attraction:
        #     params["type"] = preference
        # else:
        #     params["type"] = place_type
        #     params["keyword"] = preference

        # response = requests.get(self.base_places_url, params=params).json()

        # if "results" in response and response["results"]:
        #     places = [
        #         {
        #             "name": place.get("name", "N/A"),
        #             "place_id": place.get("place_id", ""),
        #             "coords": [place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]],
        #             "rating": place.get("rating", "N/A")
        #         }
        #         for place in response["results"][:5]    # Limit to top 5 results
        #         if "place_id" in place and place["place_id"]
        #     ]

        #     return places
        # else:
        #     print(f" No {place_type} places found near {location}")
        #     return []
    
    # async def _get_place_details_async(self, places):
    #     detailed_places = []

    #     async with aiohttp.ClientSession() as session:
    #         tasks = []
    #         for place in places:
    #             if "place_id" not in place or not place["place_id"]:
    #                 continue
                
    #             params = {
    #                 "place_id": place["place_id"],
    #                 "fields": "name,formatted_address,formatted_phone_number,rating,opening_hours",
    #                 "key": self.google_api_key
    #             }

    #             # url = "https://maps.googleapis.com/maps/api/place/details/json"
    #             url = f"{self.details_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    #             # tasks.append(self._fetch_detail(session, url, params, place))
    #             tasks.append(self._fetch_detail(session, url, place))

            # detailed_places = await asyncio.gather(*tasks)
            # return [p for p in detailed_places if p] # Remove None results
        #     results = await asyncio.gather(*tasks)
        #     for result in results:
        #         if result:
        #             detailed_places.append(result)

        # return detailed_places
        
    
    
    # async def _fetch_detail(self, session, url, params, place):
    #     async with session.get(url, params=params) as resp:
    #         data = await resp.json()
    #         if "result" in data:
    #             r = data["result"]
    #             return {
    #                 "name": r.get("name", "N/A"),
    #                 "address": r.get("formatted_address", "N/A"),
    #                 "phone_number": r.get("formatted_phone_number", "N/A"),
    #                 "rating": r.get("rating", "N/A"),
    #                 "opening_hours": r.get("opening_hours", {}).get("weekday_text", "N/A"),
    #                 "coords": place.get("coords"),
    #                 "place_id": place["place_id"]
    #             }
            
    #         return None
        
    # def _get_place_details(self, places):
    #     """ Fetch detailed information for given places using Google Places API """
    #     detailed_places = []
    #     for place in places:

    #         if "place_id" not in place or not place["place_id"]:
    #             print(f"Missing place_id for {place.get('name', 'Unknown')} (SKIPPING)")
    #             continue

    #         params = {
    #             "place_id": place["place_id"],
    #             "fields": "name,formatted_address,formatted_phone_number,rating,opening_hours",
    #             "key": self.google_api_key
    #         }

    #         response = requests.get(self.details_url, params=params).json()

    #         if "result" in response:
    #             place_details = response["result"]
    #             place_data = {
    #                 "name": place_details.get("name", "N/A"),
    #                 "address": place_details.get("formatted_address", "N/A"),
    #                 "phone_number": place_details.get("formatted_phone_number", "N/A"),
    #                 "rating": place_details.get("rating", "N/A"),
    #                 "opening_hours": place_details.get("opening_hours", {}).get("weekday_text", "N/A"),
    #                 "coords": place.get("coords"),
    #                 "place_id": place["place_id"]
    #             }
    #             detailed_places.append(place_data)
    #         else:
    #             print(f" No details found for {place['name']} (SKIPPING)")

    #         # Add delay to prevent hitting API rate limits
    #         time.sleep(0.5)

    #     return detailed_places

    #LEGACY END