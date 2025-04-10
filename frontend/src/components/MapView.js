import React, { useEffect, useState } from "react";
// import { MapContainer, TileLayer, Marker, Polyline, Popup, PolylineDecorator } from "react-leaflet";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
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

// const weatherIcon = new L.Icon({
//     iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
//     iconSize: [30, 30]
// });

const trafficIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
    iconSize: [30, 30]
});
// const recommendationIcon = new L.Icon({
//     iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
//     iconSize: [30, 30]
// });
// const restaurantIcon = new L.Icon({
//     iconUrl: "https://maps.google.com/mapfiles/ms/icons/orange-dot.png",
//     iconSize: [30, 30]
// });
// const hotelIcon = new L.Icon({
//     iconUrl: "https://maps.google.com/mapfiles/ms/icons/purple-dot.png",
//     iconSize: [30, 30]
// });
// const attractionIcon = new L.Icon({
//     iconUrl: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
//     iconSize: [30, 30]
// });

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
        if (!tripData?.route?.coordinates) {
            console.warn("No route coordinates available");
            return;
        }

        try {
            const routeCoordinates = tripData.route.coordinates.map(coord => [coord[0], coord[1]]);
            console.log("Route coordinates:", routeCoordinates);
            console.log("Total route coordinates:", routeCoordinates.length);
            console.log("First coordinate (origin):", routeCoordinates[0]);
            console.log("Last coordinate (destination):", routeCoordinates[routeCoordinates.length - 1]);
            console.log("Destination coords from route data:", tripData.route.destination_coords);

            if (routeCoordinates.length > 0) {
                // Get the destination coordinates from the route data or use the last coordinate
                const destinationCoords = tripData.route.destination_coords || routeCoordinates[routeCoordinates.length - 1];
                console.log("Using Destination Coordinates:", destinationCoords);

                // Use the route coordinates as is, since they already extend to the destination
                const completeRoute = [...routeCoordinates];

                setRoute(routeCoordinates);
                // Set map center to origin
                setCenter(routeCoordinates[0]);

                const newMarkers = [
                    {
                        position: completeRoute[0],
                        type: "origin",
                        info: "Starting Point"
                    },
                    {
                        position: destinationCoords,
                        type: "destination",
                        info: "Destination Point"
                    }
                ];

                // Add traffic markers if available
                if (tripData.traffic?.[0]?.estimated_stops) {
                    const stops = tripData.traffic[0].estimated_stops;
                    // console.log("Traffic stops:", stops);

                    stops.forEach((stop, index) => {
                        if (stop.coords) {
                            // console.log(`Processing stop ${index}:`, stop);
                            // Add traffic marker
                            newMarkers.push({
                                position: stop.coords,
                                type: "traffic",
                                info: `<b>Stop:</b> ${stop.stop}<br />
                                <b>Arrival:</b> ${stop.arrival_date_time}<br />
                                <b>Travel Time:</b> ${stop.travel_time}<br />
                                <b>Stop Duration:</b> ${stop.stop_duration || "Final Destination"}<br />
                                <b>Congestion:</b> ${stop.congestion_level}<br />
                                <b>Traffic Delay:</b> ${Math.round(stop.traffic_delay / 60)} minutes`
                            });
                        }
                    });
                }

                // Create a single route segment for the entire route
                setRouteSegments([{
                    position: completeRoute,
                    color: congestionColors.light
                }]);

                setMarkers(newMarkers);
            }

            
        } catch (error) {
            console.error("Error processing route coordinates:", error);
        }
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
                    : trafficIcon}
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