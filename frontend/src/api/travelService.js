import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export const getRoute = async (origin, destination, waypoints, departureTime, stopDurations, attractionPreferences) => {
    try {
        // Format the departure time to match the expected format
        const formattedDepartureTime = departureTime ? departureTime.replace("T", " ") : "now";
        
        // Create the request body according to the RouteRequest model
        const requestBody = {
            origin,
            destination,
            waypoints: waypoints || [],
            departure_time: formattedDepartureTime,
            stop_durations: stopDurations || [],
            attraction_preferences: attractionPreferences || ["museum", "shopping", "festival"]
        };
        
        const response = await axios.post(`${API_BASE_URL}/plan_trip`, requestBody);
        
        // Ensure the response has the expected structure
        if (!response.data) {
            throw new Error("Invalid response format from backend");
        }
        
        // Validate route data
        if (!response.data.route) {
            throw new Error("No route data in response");
        }

        // The backend returns route_info as a list, so we need to handle that
        const routeInfo = Array.isArray(response.data.route) ? response.data.route[0] : response.data.route;
        
        if (!routeInfo) {
            throw new Error("No valid route information found");
        }

        // Check if coordinates and polyline exist in the response
        const hasCoordinates = Array.isArray(routeInfo.coordinates) && routeInfo.coordinates.length > 0;
        const hasPolyline = typeof routeInfo.polyline === 'string' && routeInfo.polyline.length > 0;

        if (routeInfo.error) {
            throw new Error(`Route error: ${routeInfo.error}`);
        }

        if (!hasCoordinates || !hasPolyline) {
            throw new Error("Route data is incomplete");
        }
        
        // Return the data with the correct structure
        return {
            ...response.data,
            route: routeInfo
        };
    } catch (error) {
        console.error("Error in getRoute:", error);
        if (error.response) {
            console.error("Error response data:", error.response.data);
            console.error("Error response status:", error.response.status);
            console.error("Error response headers:", error.response.headers);
        } else if (error.request) {
            console.error("Error request:", error.request);
        }
        throw error;
    }
};

// export const getRecommendations = async (locations, preferences) => {
//     try {
//         const response = await axios.post(`${API_BASE_URL}/recommendations/`, {
//             locations,
//             preferences,
//         });
//         return response.data;
//     } catch (error) {
//         console.error("Error fetching recommendations:", error);
//         if (error.response) {
//             console.error("Error response data:", error.response.data);
//             console.error("Error response status:", error.response.status);
//         }
//         return null;
//     }
// };