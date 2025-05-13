import React, { useState } from "react";
import TripPlannerForm from "../components/TripPlannerForm";
import MapView from "../components/MapView";
import { getRoute } from "../api/travelService";

const NewHome = () => {
    const [showForm, setShowForm] = useState(true);
    const [tripData, setTripData] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (formData) => {
        try {
            setError(null);
            const data = await getRoute(
                formData.origin,
                formData.destination,
                formData.waypoints,
                formData.departureTime,
                formData.stopDurations,
                formData.attractionPreferences
            );
            setTripData(data);
            setShowForm(false);  // Hide the form when we have data
        } catch (err) {
            setError(err.message);
            console.error("Error planning trip:", err);
        }
    };

    return (
        <div className="home-container">
            {showForm && (
                <div className="form-container">
                    <TripPlannerForm onSubmit={handleSubmit} />
                </div>
            )}
            {error && <div className="error-message">{error}</div>}
            {tripData && <MapView tripData={tripData} />}
        </div>
    );
};

export default NewHome; 