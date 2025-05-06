import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export const getRoute = async (origin, destination, waypoints, departureTime) => {
    try {
        // Format the departure time to match the expected format
        const formattedDepartureTime = departureTime ? departureTime.replace("T", " ") : "now";

        // Create the request body according to the RouteRequest model
        const requestBody = {
            origin,
            destination,
            waypoints,
            departure_time: formattedDepartureTime,
            stop_durations: [], // Default empty array
            attraction_preferences: ["museum", "shopping", "festival"] // Default preferences
        };

        console.log("Sending request to backend:", requestBody);

        const response = await axios.post(`${API_BASE_URL}/plan_trip`, requestBody);
        // const response = await axios.post(`${API_BASE_URL}/route/`, {
        //     origin,
        //     destination,
        //     waypoints,
        //     departureTime,
        // });

        console.log("Response from backend:", response.data);
        
        return response.data;
    } catch (error) {
        console.error("Error fetching route:", error);
        return null;
    }
};

export const getRecommendations = async (locations, preferences) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/recommendations/`, {
            locations,
            preferences,
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        return null;
    }
};