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
weather_agent = None  # Initialize lazily
recommendation_agent = None  # Initialize lazily
logger = logging.getLogger(__name__)

def get_weather_agent():
    """Get weather agent instance, initializing it if needed"""
    global weather_agent
    if weather_agent is None:
        try:
            weather_agent = WeatherAgent()
        except ValueError as e:
            logger.warning(f"Weather agent initialization failed: {e}")
            return None
    return weather_agent

def get_recommendation_agent():
    """Get recommendation agent instance, initializing it if needed"""
    global recommendation_agent
    if recommendation_agent is None:
        try:
            recommendation_agent = RecommendationAgent()
        except ValueError as e:
            logger.warning(f"Recommendation agent initialization failed: {e}")
            return None
    return recommendation_agent

@router.get("/api/test", response_model=dict)
async def test_endpoint():
    """ Simple test endpoint to verify API is working """
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": time.time()
    }

@router.post("/api/plan_trip", response_model=dict)
async def plan_trip(request: RouteRequest):
    """ AI-powered trip planner that integrates route, weather, and recommendations """
    try:
        # logger.info(f"Received trip planning request: {request}")
        start_time = time.time()

        waypoints_list = request.waypoints
        departure_time = request.departure_time
        stop_durations = [d for d in request.stop_durations] if request.stop_durations else []

        # Fetch optimized route with timeout
        logger.info(f"Fetching route from {request.origin} to {request.destination}")
        try:
            route_info = await asyncio.wait_for(
                asyncio.to_thread(travel_agent.get_route, request.origin, request.destination, request.waypoints),
                timeout=30.0 # 30 second timeout for route
            )
        except asyncio.TimeoutError:
            logger.error("Route request timed out after 30 seconds")
            return {"error": "Route request timed out. Please try again."}
        
        logger.info(f"Route info received: {route_info}")

        # Check if route request failed
        if "error" in route_info:
            logger.error(f"Route request failed: {route_info["error"]}")
            return {"error": f"Failed to get route: {route_info["error"]}"}
        
        if "polyline" in route_info:
            # Use detailed coordinates if available, otherwise decode the polyline
            if "detailed_coordinates" in route_info:
                decoded_coordinates = route_info["detailed_coordinates"]
                logger.info(f"Using {len(decoded_coordinates)} detailed coordinates from route")
            else:
                decoded_coordinates = polyline.decode(route_info["polyline"])
                decoded_coordinates = [list(coord) for coord in decoded_coordinates]
                logger.info(f"Decoded {len(decoded_coordinates)} coordinates from polyline")
        else:
            decoded_coordinates = []
            logger.warning("No polyline found in route response")

        route_info["coordinates"] = decoded_coordinates

        if not isinstance(route_info, list):
            route_info = [route_info] if route_info else []

        # Fetch weather alerts with timeout
        weather_stops = [request.origin]
        if request.waypoints:
            weather_stops.extend(request.waypoints)
        weather_stops.append(request.destination)
        
        # Create weather request data with required structure
        weather_request = {
            "waypoints": weather_stops,
            "legs": route_info[0] if isinstance(route_info, list) else route_info
        }

        try:
            weather_agent_instance = get_weather_agent()
            if weather_agent_instance:
                weather_data = await asyncio.wait_for(
                    weather_agent_instance.get_weather(weather_request),
                    timeout=60.0 # 60 second timeout for weather
                )
            else:
                logger.warning("Weather agent not available - skipping weather data")
                weather_data = {"error": "Weather API key not configured"}
        except asyncio.TimeoutError:
            logger.error("Weather request timed out after 60 seconds")
            weather_data = {"error": "Weather request timed out"}
        
        # Get recommendations for waypoints with timeout
        try:
            recommendation_agent_instance = get_recommendation_agent()
            if recommendation_agent_instance:
                recommendations = await asyncio.wait_for(
                    recommendation_agent_instance.get_recommendations(
                        (request.waypoints or []) + [request.destination], # Exclude origin
                        request.attraction_preferences
                    ),
                    timeout=90.0 # 90 second timeout for recommendations
                )
            else:
                logger.warning("Recommendation agent not available - skipping recommendations")
                recommendations = {"error": "Google Maps API key not configured"}
        except asyncio.TimeoutError:
            logger.error("Recommendations request timed out after 90 seconds")
            recommendations = {"error": "Recommendations request timed out"}
        
        # Get attractions along the route with timeout
        try:
            recommendation_agent_instance = get_recommendation_agent()
            if recommendation_agent_instance:
                route_attractions = await asyncio.wait_for(
                    recommendation_agent_instance.get_route_attractions(
                        decoded_coordinates,
                        request.attraction_preferences
                    ),
                    timeout=60.0 # 60 second timeout for route attractions
                )
            else:
                logger.warning("Recommendation agent not available - skipping route attractions")
                route_attractions = []
        except asyncio.TimeoutError:
            logger.error("Route attractions request timed out after 60 seconds")
            route_attractions = []
        
        # Add route attractions to the response
        for route_info_item in route_info:
            route_info_item["route_attractions"] = route_attractions

        # Prepare the response
        response_data = {
            "route": route_info,
            "weather": weather_data,
            "recommendations": recommendations
        }

        # Log response structure for debugging
        logger.info(f"Response structure:")
        logger.info(f"- Route keys: {list(route_info[0].keys()) if route_info and isinstance(route_info, list) else 'No route'}")
        logger.info(f"- Weather keys: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'No weather'}")
        logger.info(f"- Recommendations keys: {list(recommendations.keys()) if isinstance(recommendations, dict) else 'No recommendations'}")

        # Check for large data that might cause Swagger issues
        if route_info and isinstance(route_info, list) and len(route_info) > 0:
            route_item = route_info[0]
            if 'coordinates' in route_item:
                logger.info(f"- Route coordinates count: {len(route_item['coordinates'])}")
            if 'route_attractions' in route_item:
                logger.info(f"- Route attractions count: {len(route_item['route_attractions'])}")
        # Log total response time
        response_str = json.dumps(response_data, default=str)
        logger.info(f"Response size: {len(response_str)} characters")

        logger.info(f"Trip planning completed in {time.time() - start_time:.2f} seconds")
        return response_data
    
    except Exception as e:
        error_msg = f"Error in plan_trip: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)  # Also print to console for immediate visibility
        return {"error": "Failed to process the trip request", "details": str(e)}
