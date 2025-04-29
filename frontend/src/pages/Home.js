import React, { useState } from "react";
import TripForm from "../components/TripForm";
// import TripPlannerForm from "../components/TripPlannerForm";
import MapView from "../components/MapView";
import { getRoute } from "../api/travelService";

const Home = () => {
    const [route, setRoute] = useState([]);
    const [waypoints, setWaypoints] = useState([]);

    const handleTripSubmit = async (tripData) => {
        // console.log("Sending API Request:", tripData);

        const data = await getRoute(tripData.origin, tripData.destination, [], tripData.departureTime);

        if (data) {
            console.log("API Response:", data);
            setRoute(data.polyline);
            setWaypoints(data.waypoints);
        } else {
            console.error("Error fetching route");
        };
    };

    return (
        <div>
            <h2>Plan Your Trip!</h2>
            {/* <TripForm onSubmit={handleTripSubmit} /> */}
            <TripForm onSubmit={handleTripSubmit} />
            <MapView route={[]} waypoints={waypoints} />
        </div>
    );
};

export default Home;