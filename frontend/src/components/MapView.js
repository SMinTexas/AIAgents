import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Custom marker icons
const originIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-pushpin.png",
    iconSize: [30, 30]
})

const destinationIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-pushpin.png",
    iconSize: [30, 30]
})

const weatherIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
    iconSize: [30, 30]
});
const trafficIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
    iconSize: [30, 30]
})
const recommendationIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
    iconSize: [30, 30]
})

const restaurantIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    iconSize: [30, 30]
});

const hotelIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/purple-dot.png",
    iconSize: [30, 30]
});

const attractionIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
    iconSize: [30, 30]
});

const MapView = ({ tripData }) => {
    const [center, setCenter] = useState([29.7858, -95.8244]); // Default to Katy, TX
    const [route, setRoute] = useState([]);
    const [markers, setMarkers] = useState([]);

    useEffect(() => {
        const renderStart = performance.now();

        if (!tripData || !tripData.route) {
            console.warn("No route data received in frontend");
            return;
        }

        if (!tripData?.route?.coordinates || !Array.isArray(tripData.route.coordinates)) {
            console.warn("No valid route coordinates available");
            return;
        }

        const routeCoordinates = tripData.route.coordinates.map(coord => [coord[0], coord[1]]);
        setRoute(routeCoordinates);

        // Set map center to origin
        const originCoords = routeCoordinates[0] || [29.7858, -95.8244];
        const destinationCoords = routeCoordinates[routeCoordinates.length - 1] || null;
        setCenter(originCoords);

        // Add markers for waypoints, weather, traffic, and recommendations
        const newMarkers = [];

        if (originCoords) {
            newMarkers.push({
                position: originCoords,
                type: "origin",
                info: "Starting Point"
            });
        } else {
            console.warn("No origin coordinates found in route data");
        }

        if (destinationCoords) {
            newMarkers.push({
                position: destinationCoords,
                type: "destination",
                info: "Destination Point"
            });
        } else {
            console.warn("No destination coordinates found in route data");
        }

        // Weather markers
        if (tripData.weather) {
            Object.entries(tripData.weather).forEach(([location, data]) => {
                if (data && data.coords) {
                    newMarkers.push({
                        position: data.coords,
                        type: "weather",
                        info: `${data.condition}, ${data.temperature}`
                    });
                }
            });
        } else {
            console.warn("No valid weather data found.");
        }

        // Traffic markers
        if (tripData.traffic?.[0]?.estimated_stops) {
            tripData.traffic[0].estimated_stops.forEach((stop) => {
                if (stop.coords) {
                    newMarkers.push({
                        position: stop.coords,
                        type: "traffic",
                        info: `<b>Stop:</b> ${stop.stop}<br />
                            <b>Arrival:</b> ${stop.arrival_date_time}<br />
                            <b>Travel Time:</b> ${stop.travel_time}<br />
                            <b>Stop Duration:</b> ${stop.stop_duration || "Final Destination"}
                        `
                    });
                }
            });
        } else {
            console.warn("No valid traffic data found.");
        }

        // Recommendation markers
        if (tripData.recommendations) {
            Object.entries(tripData.recommendations).forEach(([city, recs]) => {
                console.log(`City: ${city}`, recs);
                const categories = ["restaurants", "hotels", "attractions"];
                try {
                    categories.forEach((category) => {
                        const items = recs[category];
                        if (Array.isArray(items)) {
                            items.forEach((item) => {
                                if (item.coords) {
                                    newMarkers.push({
                                        position: item.coords,
                                        type: "recommendation",
                                        subtype: category,
                                        info: `${item.name}<br>Type: ${category}<br>Rating: ${item.rating || "N/A"}<br>Address: ${item.address || "N/A"}<br>Phone: ${item.phone_number || "N/A"}`
                                    });
                                }
                            });
                        }
                    });
                } catch (error) {
                    console.error("Error while building recommendation markers:", error);   
                }
            });
        } else {
            console.warn("No valid recommendations found");
        }

        setMarkers(newMarkers);
        const renderEnd = performance.now();
    }, [tripData]);

    return (
        <MapContainer center={center} zoom={6} style={{ height: "100vh", width: "100%" }}>
            {/* Map tile layer */}
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

            {/* Route polyline */}
            {route.length > 1 && <Polyline positions={route} color="blue" />}

            {/* Markers for waypoints, weather, traffic, and recommendations */}
            {markers.map((marker, index) => (
                <Marker
                    key={index}
                    position={marker.position}
                    icon={marker.type === "origin" 
                    ? originIcon 
                    : marker.type === "destination"
                    ? destinationIcon
                    : marker.type === "weather"
                    ? weatherIcon
                    : marker.type === "traffic" 
                    ? trafficIcon 
                    : marker.type === "recommendation" && marker.subtype === "restaurants"
                    ? restaurantIcon
                    : marker.type === "recommendation" && marker.subtype === "hotels"
                    ? hotelIcon
                    : marker.type === "recommendation" && marker.subtype === "attractions"
                    ? attractionIcon
                    : recommendationIcon
                }
                >
                    <Popup>
                        <div dangerouslySetInnerHTML={{ __html: marker.info }} />
                    </Popup>  
                </Marker>  
            ))}
        </MapContainer>
    );
};

export default MapView;