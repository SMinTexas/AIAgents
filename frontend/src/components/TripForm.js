import React, { useState } from "react";
console.log("TripForm component loaded - NEW VERSION");
const TripForm = ({ onSubmit }) => {
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [waypoints, setWaypoints] = useState([""]);
    const [departureTime, setDepartureTime] = useState("");
    const [errors, setErrors] = useState({});

    const validateForm = () => {
        const newErrors = {};

        if (!origin.trim()) {
            newErrors.origin = "Starting location is required.";
        }

        if (!destination.trim()) {
            newErrors.destination = "Destination is required.";
        }

        if (!departureTime) {
            newErrors.departureTime = "Departure time is required.";
        }

        // Validate waypoints (only non-empty waypoints)
        const nonEmptyWaypoints = waypoints.filter(wp => wp.trim());
        if (nonEmptyWaypoints.length > 0) {
            nonEmptyWaypoints.forEach((waypoint, index) => {
                if (!waypoint.trim()) {
                    newErrors[`waypoint${index}`] = "Waypoint cannot be empty.";
                }
            });
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // Filter out empty waypoints and trim whitespace
        const filteredWaypoints = waypoints
            .filter(waypoint => waypoint.trim() !== "")
            .map(waypoint => waypoint.trim());

        const tripData = {
            origin: origin.trim(),
            destination: destination.trim(),
            waypoints: filteredWaypoints,
            departureTime: departureTime
        };

        console.log("Submitting trip:", tripData);
        onSubmit(tripData);
    }

    const addWaypoint = () => {
        setWaypoints([...waypoints, ""]);
    };

    const removeWaypoint = (index) => {
        const newWaypoints = [...waypoints];
        newWaypoints.splice(index, 1);
        setWaypoints(newWaypoints);

        // Clear any error for the removed waypoint
        const newErrors = { ...errors };
        delete newErrors[`waypoints${index}`];
        setErrors(newErrors);
    };

    const updateWaypoint = (index, value) => {
        const newWaypoints = [...waypoints];
        newWaypoints[index] = value;
        setWaypoints(newWaypoints);

        // Clear error when user starts typing
        if (errors[`waypoint${index}`]) {
            const newErrors = { ...errors };
            delete newErrors[`waypoint${index}`];
            setErrors(newErrors);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="trip-form">
            <h3>Plan Your Trip</h3>
            {/* <input
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
            <button type="submit">Plan Trip</button> */}

            <div className="form-group">
                <label htmlFor="origin">Starting Location</label>
                <input 
                    id="origin"
                    type="text"
                    placeholder="e.g. Houston, TX"
                    value={origin}
                    onChange={(e) => {
                        setOrigin(e.target.value);
                        if (errors.origin) {
                            setErrors({ ...errors, origin: null });
                        }
                    }}
                    className={errors.origin ? "error" : ""}
                />
                {errors.origin && <span className="error-message">{errors.origin}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="destination">Destination Location</label>
                <input 
                    id="destination"
                    type="text"
                    placeholder="e.g. Atlanta, GA"
                    onChange={(e) => {
                        setDestination(e.target.value);
                        if (errors.destination) {
                            setErrors({ ...errors, destination: null});
                        }
                    }}
                    className={errors.destination ? "error" : ""}
                />
                {errors.destination && <span className="error-message">{errors.destination}</span>}
            </div>

            <div className="form-group">
                <label>Waypoints (Optional)</label>
                {waypoints.map((waypoint, index) => (
                    <div key={index} className="waypoint-input">
                        <input 
                            type="text"
                            placeholder={`Waypoint ${index + 1} (e.g. New Orleans, LA)`}
                            value={waypoint}
                            onChange={(e) => updateWaypoint(index, e.target.value)}
                            className={errors[`waypoint${index}`] ? "error" : ""}
                        />
                        {waypoints.length > 1 && (
                            <button
                                type="button"
                                className="remove-waypoint"
                                onClick={() => removeWaypoint(index)}
                            >Remove</button>
                        )}
                        {errors[`waypoint${index}`] && <span className="error-message">{errors[`waypoint${index}`]}</span>}
                    </div>
                ))}
                <button
                    type="button"
                    className="add-waypoint"
                    onClick={addWaypoint}>Add waypoint</button>
            </div>

            <div className="form-group">
                <label htmlFor="departureTime">Departure Time</label>
                <input
                    id="departureTime"
                    type="datetime-local"
                    value={departureTime}
                    onChange={(e) => {
                        setDepartureTime(e.target.value);
                        if (errors.departureTime) {
                            setErrors({ ...errors, departureTime: null });
                        }
                    }}
                    className={errors.departureTime ? "error" : ""}
                />
                {errors.departureTime && <span className="error-message">{errors.departureTime}</span>}
            </div>

            <button type="submit" className="submit-button">Plan Trip</button>
        </form>
    );
};

export default TripForm;
