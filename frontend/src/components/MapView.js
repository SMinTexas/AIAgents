import React, { useEffect, useState } from "react";
// import { MapContainer, TileLayer, Marker, Polyline, Popup, PolylineDecorator } from "react-leaflet";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Custom marker icons
const originIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/star.png",
    iconSize: [30, 30]
})

const destinationIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/flag.png",
    iconSize: [30, 30]
})

const weatherIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
    iconSize: [30, 30]
});

const trafficIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
    iconSize: [30, 30]
});
const recommendationIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
    iconSize: [30, 30]
});
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

// Traffic congestion colors
const congestionColors = {
    light: "#4CAF50", // Green
    moderate: "#FFC107", // Yellow
    heavy: "#F44336", // Red
    unknown: "#9E9E9E" // Grey
};

const MapView = ({ tripData }) => {
    const defaultCenter = [29.7858, -95.8244];
    const [center, setCenter] = useState(defaultCenter);
    // const [center, setCenter] = useState([29.7858, -95.8244]); // Default to Katy, TX
    const [route, setRoute] = useState([]);
    const [markers, setMarkers] = useState([]);
    const [routeSegments, setRouteSegments] = useState([]);

    useEffect(() => {
        const renderStart = performance.now();
        // console.log("Rendering map and markers started ...");
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
        const originCoords = tripData.route?.[0]?.coordinates?.[0] || [29.7858, -95.8244];
        const destinationCoords = tripData.route?.coordinates?.[tripData.route.coordinates.length -1] || null;
        setCenter(originCoords);

        // Add markers for waypoints, weather, traffic, and recommendations
        const newMarkers = [];

        if (originCoords) {
            newMarkers.push({
                position: originCoords,
                type: "origin",
                info: "Starting Point"
            })
        }

        if (destinationCoords) {
            newMarkers.push({
                position: destinationCoords,
                type: "destination",
                info: "Destination Point"
            })
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
        // console.log(`Map and markers rendered in ${(renderEnd - renderStart).toFixed(2)} ms`);
    }, [tripData]);

    // Helper function to check if two points are near each other
    const _isNearPoint = (point1, point2, threshold = 1.0) => {
        const latDiff = Math.abs(point1[0] - point2[0]);
        const lngDiff = Math.abs(point1[1] - point2[1]);
        console.log(`Comparing points:`, {
            point1,
            point2,
            latDiff,
            lngDiff,
            threshold,
            isNear: latDiff < threshold && lngDiff < threshold
        });
        return latDiff < threshold && lngDiff < threshold;
    };

    return (
        <MapContainer
            center={center}
            zoom={6}
            style={{ height: "100vh", width: "100%" }}
        >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {/* Route segments with congestion colors */}
            {routeSegments.map((segment, index) => (
                <Polyline 
                    key={index}
                    positions={segment.positions}
                    color={segment.color}
                    weight={6}
                    opacity={0.7}
                />
            ))}

            {/* Traffic Legend */}
            <div className="traffic-legend" style={{
                position: 'absolute',
                bottom: '20px',
                right: '20px',
                backgroundColor: 'white',
                padding: '10px',
                borderRadius: '5px',
                boxShadow: '0 0 10px rgba(0,0,0,0.2)',
                zIndex: 1000
            }}>
                <h4 style={{ margin: '0 0 5px 0' }}>Traffic Congestion</h4>
                {Object.entries(congestionColors).map(([congestionLevel, color]) => (
                    <div key={congestionLevel} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                        <div style={{
                            width: '20px',
                            height: '20px',
                            backgroundColor: color,
                            marginRight: '10px'
                        }}></div>
                        <span>{congestionLevel.charAt(0).toUpperCase() + congestionLevel.slice(1)}</span>
                    </div>
                ))}
            </div>
            {markers.map((marker, index) => (
                <Marker
                key={index}
                position={marker.position}
                icon={marker.type === "origin"
                    ? originIcon
                    : marker.type === "destination"
                    ? destinationIcon
                    : marker.type === "traffic"
                    ? trafficIcon
                    : marker.type === "recommendation" && marker.subtype === "attractions"
                    ? attractionIcon
                    : marker.type === "recommendation" && marker.subtype === "hotels"
                    ? hotelIcon
                    : marker.type === "recommendation" && marker.subtype === "restaurants"
                    ? restaurantIcon
                    : recommendationIcon}
                >
                    <Popup>
                        <div dangerouslySetInnerHTML={{ __html: marker.info }} />
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    )
};

export default MapView;