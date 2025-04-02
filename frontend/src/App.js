import React, { useState, useEffect } from "react";
import MapView from "./components/MapView";
import "leaflet/dist/leaflet.css";

window.onerror = function (message, source, lineno, colno, error) {
  console.error("Global Error Caught:", message, "at", source, "line", lineno, "column", colno, error);
}

window.addEventListener("beforeunload", (event) => {
  console.log("Page is reloading!");
});

const App = () => {
  useEffect(() => {
    console.log("App component mounted");
    return () => {
      console.log("App component unmounted");
    };
  }, []);

  const [tripData, setTripData] = useState(null);
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [waypoints, setWaypoints] = useState("");
  const [departure_time, setDepartureTime] = useState("");
  const [stopDurations, setStopDurations] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isRouteLoading, setIsRouteLoading] = useState(false);
  const [attractionPrefs, setAttractionPrefs] = useState("museum,shopping,festival")

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload
    setIsRouteLoading(true); // Set loading state

    const startTime = performance.now();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/plan_trip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // body: JSON.stringify(tripRequest),
        body: JSON.stringify({
          origin,
          destination,
          waypoints: waypoints.split(';').map((wp) => wp.trim()),
          departure_time: departure_time ? departure_time.replace("T", " ") : null,
          stop_durations: stopDurations.split(',').map((d) => parseInt(d.trim(), 10)),
          attraction_preferences: attractionPrefs.split(",").map((p) => p.trim())
        }),
      });

      const data = await response.json();
      // console.log("Full API Response:", data);

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}: ${data.error}`);
      }

      setTripData({
        ...data,
        route: Array.isArray(data.route) ? data.route[0] : data.route,
        traffic: data.traffic,
        recommendations: data.recommendations || {},
      })
    } catch (error) {
      console.error("Error in handleSubmit:", error);
      setErrorMessage(error.message);
    } finally {
      const endTime = performance.now();
      // console.log(`Trip data received and set in state.  Total fetch time: ${(endTime - startTime).toFixed(2)} ms`);
      setIsRouteLoading(false); // Reset loading state
    }
  };

  return (
    <div>
      <h1>AI Travel Planner</h1>

      {/* Input Form */}
      <form>
        <label>Origin:</label>
        <input
          type="text"
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
        />
        <label>Destination:</label>
        <input
          type="text"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
        />
        <label>Waypoints (separate by `;`):</label>
        <input
          type="text"
          value={waypoints}
          onChange={(e) => setWaypoints(e.target.value)}
        />
        <label>Departure Date/Time:</label>
        <input
          type="datetime-local"
          value={departure_time}
          onChange={(e) => setDepartureTime(e.target.value)}
        />
        <label>Stop Durations (comma-separated in hours):</label>
        <input
          type="text"
          value={stopDurations}
          onChange={(e) => setStopDurations(e.target.value)}
        />
        <label>Attraction Preferences (comma-separated):</label>
        <input
          type="text"
          value={attractionPrefs}
          onChange={(e) => setAttractionPrefs(e.target.value)}
        />

        <button type="button" onClick={handleSubmit}>Plan Trip</button>
      </form>

      {/* Map Component */}
      {/* {isRouteLoading ? (
        <p>Loading route ...</p>
      ) : tripData && 
          tripData.route && 
          Array.isArray(tripData.route.coordinates) &&
          tripData.route.coordinates.length > 0 ? (
          <MapView tripData={tripData} /> 
      ) : null} */}

      {isRouteLoading ? (
        <p>Loading route ...</p>
      ) : tripData ? (
        <MapView tripData={tripData} />
      ) : null}
    </div>
  )
}

export default App;
