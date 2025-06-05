from pydantic import BaseModel, Field
from typing import List, Optional

# ==============================================
# Request Models (input data)
# ==============================================

class RouteRequest(BaseModel):
    origin: str = Field(..., title="Origin", description="Starting point address", example="Katy, TX")
    destination: str = Field(..., title="Destination", description="Ending point address", example="Lake Buena Vista, FL")
    waypoints: Optional[List[str]] = Field(
        default=[],
        title="Waypoints",
        description="Intermediate stops along the route",
        example=["New Orleans, LA", "Pensacola, FL"]
    )
    departure_time: str = Field(
        default="now", title="Departure Time", description="Planned departure time in format YYYY-MM-DD HH:MM",
        example="2025-05-01 05:00"
    )
    stop_durations: Optional[List[int]] = Field(
        default=[],
        title="Stop Durations",
        description="Duration of each stop in minutes",
        example=[4, 12]
    )
    attraction_preferences: Optional[List[str]] = Field(
        default=["museum", "restaurant", "shopping_mall"],
        title="Attraction Preferences",
        description="Types of attractions to include in recommendations",
        example=["museum", "restaurant", "hotel"]
    )

class DepartureTimeRequest(BaseModel):
    origin: str = Field(..., title="Origin", description="Starting point address", example="Katy, TX")
    destination: str = Field(..., title="Destination", description="Ending point address", example="Orlando, FL")
    waypoints: Optional[List[str]] = Field(
        default=[],
        title="Waypoints",
        description="Intermediate stops along the route",
        example=["New Orleans, LA", "Pensacola, FL"]
    )
    departure_time: int = Field(..., title="Departure Time", description="Planned time of departure", example="05:00 AM")

# ==============================================
# Response Models (output data)
# ==============================================
    
class RouteLeg(BaseModel):
    start_address: str = Field(..., title="Start Address", description="Starting address of the leg", example="Katy, TX")
    end_address: str = Field(..., title="End Address", description="Ending address of the leg", example="New Orleans, LA")
    distance_text: str = Field(..., title="Distance Text", description="Distance of the leg", example="300 miles")
    duration_text: str = Field(..., title="Duration Text", description="Duration of the leg", example="5 hours")

class RouteResponse(BaseModel):
    total_distance_miles: float = Field(..., title="Total Distance (miles)", description="Total distance of the route in miles", example=1500.25)
    total_distance_text: str = Field(..., title="Total Distance (text)", description="Formatted total distance of the route in miles", example="1,500 miles")
    estimated_time_hours: float = Field(..., title="Estimated Time (hours)", description="Estimated time to travel the route in hours", example=24.5)
    estimated_time_text: str = Field(..., title="Estimated Time (text)", description="Formatted estimated time to travel the route in hours and minutes", example="24 hours 30 minutes")
    polyline: str = Field(..., title="Encoded Polyline", description="Polyline for drawing the route on a map")
    legs: List[RouteLeg] = Field(default=[], title="Route Legs", description="Detailed breakdown of each segment of the trip")
    waypoints: List[str] = Field(default=[], title="Waypoints", description="Intermediate stops along the route", example=["New Orleans, LA", "Pensacola, FL"])

