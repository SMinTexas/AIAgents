from fastapi import APIRouter, Query
import polyline
from models import RouteRequest
from agents.agent import TravelAgent
from agents.weather_agent import WeatherAgent
from agents.recommendation_agent import RecommendationAgent
import traceback
import json
import asyncio
import time
import logging

router = APIRouter()
travel_agent = TravelAgent()
weather_agent = WeatherAgent()
recommendation_agent = RecommendationAgent()
logger = logging.getLogger(__name__)

@router.post("/api/plan_trip", response_model=dict)
async def plan_trip(request: RouteRequest):
    """ AI-powered trip planner that integrates route, weather, and recommendations """
    try:
        # print(f"\n Incoming API request: {request}")
        start_time = time.time()

        waypoints_list = request.waypoints
        departure_time = request.departure_time
        stop_durations = [d for d in request.stop_durations] if request.stop_durations else []

        # Fetch optimized route
        route_info = travel_agent.get_route(request.origin, request.destination, request.waypoints)

        if "polyline" in route_info:
            decoded_coordinates = polyline.decode(route_info["polyline"])
            decoded_coordinates = [list(coord) for coord in decoded_coordinates]
        else:
            decoded_coordinates = []
            print ("No polyline found in route response")

        route_info["coordinates"] = decoded_coordinates

        if not isinstance(route_info, list):
            route_info = [route_info] if route_info else []

        # Fetch weather alerts
        weather_stops = [request.origin]
        if request.waypoints:
            weather_stops.extend(request.waypoints)
        weather_stops.append(request.destination)
        
        logger.info(f"Fetching weather for stops: {weather_stops}")
        weather_info = await weather_agent.get_weather({
            "waypoints": weather_stops,
            "legs": route_info[0] if isinstance(route_info, list) else route_info  # Pass the route info to ensure we have all stops
        })

        # Ensure destination is included in weather lookup
        if request.destination not in weather_info:
            logger.info(f"Destination {request.destination} not in weather info, fetching separately")
            dest_weather = await weather_agent.get_weather({"waypoints": [request.destination]})
            if isinstance(dest_weather, dict):
                weather_info.update(dest_weather)
                logger.info("Added destination weather data")

        # Fetch AI-driven recommendations for food, lodging, and activities
        recommendations = await recommendation_agent.get_recommendations(request.waypoints)

        response_data = {
            "route": route_info,
            "weather": weather_info,
            "recommendations": recommendations
        }

        # print(f"Backend trip planning completed in {time.time() - start_time:.2f} seconds")
        return response_data
    
    except Exception as e:
        print(f"\n ERROR in `plan_trip`: {str(e)}")
        traceback.print_exc()
        return {"error": "Failed to process the trip request"}
