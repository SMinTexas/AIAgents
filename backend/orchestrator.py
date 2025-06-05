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
        # logger.info(f"Received trip planning request: {request}")
        start_time = time.time()

        waypoints_list = request.waypoints
        departure_time = request.departure_time
        stop_durations = [d for d in request.stop_durations] if request.stop_durations else []

        # Fetch optimized route
        # logger.info(f"Fetching route from {request.origin} to {request.destination}")
        route_info = travel_agent.get_route(request.origin, request.destination, request.waypoints)
        # logger.info(f"Route info received: {route_info}")

        if "polyline" in route_info:
            decoded_coordinates = polyline.decode(route_info["polyline"])
            decoded_coordinates = [list(coord) for coord in decoded_coordinates]
            # logger.info(f"Decoded {len(decoded_coordinates)} coordinates from polyline")
        else:
            decoded_coordinates = []
            # logger.warning("No polyline found in route response")

        route_info["coordinates"] = decoded_coordinates

        if not isinstance(route_info, list):
            route_info = [route_info] if route_info else []

        # Fetch weather alerts
        weather_stops = [request.origin]
        if request.waypoints:
            weather_stops.extend(request.waypoints)
        weather_stops.append(request.destination)
        
        # Create weather request data with required structure
        weather_request = {
            "waypoints": weather_stops,
            "legs": route_info[0] if isinstance(route_info, list) else route_info
        }
        weather_data = await weather_agent.get_weather(weather_request)
        
        # Get recommendations for waypoints
        recommendations = await recommendation_agent.get_recommendations(
            # [request.origin] + request.waypoints + [request.destination],
            request.waypoints,
            request.attraction_preferences
        )
        
        # Get attractions along the route
        route_attractions = await recommendation_agent.get_route_attractions(
            decoded_coordinates,
            request.attraction_preferences
        )
        
        # Add route attractions to the response
        for route_info_item in route_info:
            route_info_item["route_attractions"] = route_attractions

        # Prepare the response
        response_data = {
            "route": route_info,
            "weather": weather_data,
            "recommendations": recommendations
        }

        # logger.info(f"Trip planning completed in {time.time() - start_time:.2f} seconds")
        return response_data
    
    except Exception as e:
        error_msg = f"Error in plan_trip: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)  # Also print to console for immediate visibility
        return {"error": "Failed to process the trip request", "details": str(e)}
