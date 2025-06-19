import React, { useState } from "react";
import TripPlannerForm from "../components/TripPlannerForm";
import MapView from "../components/MapView";
import { getRoute } from "../api/travelService";

const Home = () => {
    const [tripData, setTripData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleTripSubmit = async (tripData) => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await getRoute(
                tripData.origin,
                tripData.destination,
                tripData.waypoints,
                tripData.departureTime
            );

            if (data) {
                // Ensure the data has the correct structure for MapView
                const formattedData = {
                    route: {
                        coordinates: data.coordinates || [],
                        polyline: data.polyline || "",
                        waypoints: data.waypoints || [],
                        legs: data.legs || [],
                        destination_coords: data.destination_coords || null
                    },
                    weather: data.weather || {},
                    traffic: data.traffic || { incidents: [] },
                    recommendations: data.recommendations || {}
                };

                setTripData(formattedData);
            } else {
                setError("Failed to fetch route data. . Please try again.");
            }
        } catch (error) {
            setError("An error occurred while planning your trip.  Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h2>Plan Your Trip!</h2>
            <TripPlannerForm onSubmit={handleTripSubmit} />
            <MapView route={[]} waypoints={waypoints} />
        </div>
    );
};

export default Home;