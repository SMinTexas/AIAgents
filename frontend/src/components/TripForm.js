import React, { useState } from "react";

const TripForm = ({ onSubmit }) => {
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [waypoints, setWaypoints] = useState([]);
    const [departureTime, setDepartureTime] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Submitting trip: ", { origin, destination, departureTime });
        onSubmit({ origin, destination, departureTime });
    }

    return (
        <form onSubmit={handleSubmit}>
            <h3>Plan Your Trip</h3>
            <input
                type="text"
                placeholder="Starting Location"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                required
            />
            <input
                type="text"
                placeholder="Destination Location"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                required
            />
            <input
                type="datetime-local"
                value={departureTime}
                onChange={(e) => setDepartureTime(e.target.value)}
                required
            />
            <button type="submit">Plan Trip</button>
        </form>
    );
};

export default TripForm;
