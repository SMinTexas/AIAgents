from fastapi import APIRouter, Query
import polyline
from models import RouteRequest
from agents.agent import TravelAgent
from agents.traffic_agent import TrafficAgent
from agents.weather_agent import WeatherAgent
from agents.recommendation_agent import RecommendationAgent
import traceback
import json
import asyncio
import time

router = APIRouter()
travel_agent = TravelAgent()
traffic_agent = TrafficAgent()
weather_agent = WeatherAgent()
recommendation_agent = RecommendationAgent()

@router.post("/api/plan_trip", response_model=dict)
async def plan_trip(request: RouteRequest):
    """ AI-powered trip planner that integrates route, traffic, weather, and recommendations """
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

        # Fetch real-time traffic data
        traffic_info = traffic_agent.get_traffic(
            request.origin, 
            request.destination, 
            request.waypoints, 
            departure_time, 
            stop_durations
        )

        if not isinstance(traffic_info, list):
            traffic_info = [traffic_info] if traffic_info else []

        # Fetch weather alerts
        weather_stops = [request.origin] + waypoints_list + [request.destination]
        weather_info = weather_agent.get_weather({
            "waypoints": weather_stops
        })

        # Ensure destination is included in weather lookup
        # if request.destination not in weather_info:
        #     dest_weather = weather_agent.get_weather({"waypoints": [request.destination]})
        #     if isinstance(dest_weather, list):
        #         weather_info.update(dest_weather)

        # Fetch AI-driven recommendations for food, lodging, and activities
        # recommendations = await recommendation_agent.get_recommendations(request.waypoints)
        recommendations = await recommendation_agent.get_recommendations(
            request.waypoints
            # food_preference="Any",
            # lodging_preference="hotel",
            # attraction_preference=request.attraction_preferences or ["museum"]
        )

        # if not isinstance(recommendations, list):
        #     recommendations = [recommendations] if recommendations else []

        response_data = {
            "route": route_info,
            "traffic": traffic_info,
            "weather": weather_info,
            "recommendations": recommendations
        }

        # print(f"\n Final Traffic Object (before return)")
        # print(json.dumps(traffic_info, indent=2))
        # print(f"Backend trip planning completed in {time.time() - start_time:.2f} seconds")
        return response_data
    
    except Exception as e:
        print(f"\n ERROR in `plan_trip`: {str(e)}")
        traceback.print_exc()
        return {"error": "Failed to process the trip request"}
