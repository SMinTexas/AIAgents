import React, { useState } from "react";
import TripForm from "../components/TripForm";
// import TripPlannerForm from "../components/TripPlannerForm";
import MapView from "../components/MapView";
import { getRoute } from "../api/travelService";

// const Home = () => {
//     const [route, setRoute] = useState([]);
//     const [waypoints, setWaypoints] = useState([]);

//     const handleTripSubmit = async (tripData) => {
//         // console.log("Sending API Request:", tripData);

//         const data = await getRoute(tripData.origin, tripData.destination, [], tripData.departureTime);

//         if (data) {
//             console.log("API Response:", data);
//             setRoute(data.polyline);
//             setWaypoints(data.waypoints);
//         } else {
//             console.error("Error fetching route");
//         };
//     };

//     return (
//         <div>
//             <h2>Plan Your Trip!</h2>
//             {/* <TripForm onSubmit={handleTripSubmit} /> */}
//             <TripForm onSubmit={handleTripSubmit} />
//             <MapView route={[]} waypoints={waypoints} />
//         </div>
//     );
// };
const Home = () => {
    const [tripData, setTripData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleTripSubmit = async (tripData) => {
        console.log("Sending API request:", tripData);
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
                console.log("API Response:", data);

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

                console.log("Formatted data for MapView:", formattedData);
                setTripData(formattedData);
            } else {
                console.error("Error fetching data");
                setError("Failed to fetch route data. . Please try again.");
            }
        } catch (error) {
            console.error("Error in handleTripSubmit:", error);
            setError("An error occurred while planning your trip.  Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h2>Plan Your Trip!</h2>
            <TripForm onSubmit={handleTripSubmit} />
            
            {isLoading && <p>Loading route data ...</p>}
            {error && <p className="error-message">{error}</p>}

            {tripData && (
                <MapView tripData={tripData} />
            )}
        </div>
    );
};

export default Home;