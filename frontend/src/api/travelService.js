import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export const getRoute = async (origin, destination, waypoints, departureTime) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/route/`, {
            origin,
            destination,
            waypoints,
            departureTime,
        });

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