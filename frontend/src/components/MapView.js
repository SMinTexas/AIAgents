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

const weatherIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/purple-pushpin.png",
    iconSize: [30, 30]
});

const trafficIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    iconSize: [30, 30]
});

const recommendationIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
    iconSize: [30, 30]
});

const waypointIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/purple-pushpin.png",
    iconSize: [30, 30]
})
const restaurantIcon = new L.Icon({
    iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
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
    // Default center coordinates (will be updated when route data is available)
    const defaultCenter = [39.8283, -98.5795];
    const [center, setCenter] = useState(defaultCenter);
    const [route, setRoute] = useState([]);
    const [markers, setMarkers] = useState([]);
    const [routeSegments, setRouteSegments] = useState([]);
    const [mapBounds, setMapBounds] = useState(null);

    useEffect(() => {
        const renderStart = performance.now();
        setRoute([]);
        setMarkers([]);
        setRouteSegments([]);
        setCenter(defaultCenter);
        setMapBounds(null);

        if (!tripData || !tripData.route || !tripData.route.coordinates || !Array.isArray(tripData.route.coordinates) || tripData.route.coordinates.length === 0) {
            console.warn("No valid route data available");
            return;
        }
        
        try {
            const routeCoordinates = tripData.route.coordinates
                .filter(coord => Array.isArray(coord) && coord.length >= 2)
                .map(coord => [coord[0], coord[1]]);

            if (routeCoordinates.length === 0) {
                console.warn("No valid route coordinates after filtering");
                return;
            }

            // Get the destination coordinates from the route data or use the last coordinate
            const destinationCoords = tripData.route.destination_coords || routeCoordinates[routeCoordinates.length - 1];

            // Use the route coordinates as is
            setRoute(routeCoordinates);

            // Set map center to origin (first coordinate of the route)
            setCenter(routeCoordinates[0]);

            // Create a bounds object to fit all markers
            const bounds = L.latLngBounds(routeCoordinates);
            setMapBounds(bounds);

            // Add origin and destination markers
            console.log(tripData.route);
            console.log(destinationCoords);
            var lastIndex = tripData.route.legs.length - 1;
            const newMarkers = [
                {
                    position: routeCoordinates[0],
                    type: "origin",
                    info: `<b>Starting Point:</b> ${tripData.route.legs[0].start_address}`
                },
                {
                    position: destinationCoords,
                    type: "destination",
                    info: `<b>Destination:</b> ${tripData.route.legs[lastIndex].end_address}`
                }
            ];

            // Add waypoint markers if available
            if (tripData.route.waypoints && Array.isArray(tripData.route.waypoints) && tripData.route.waypoints.length > 0) {
                // Get the legs from the route data
                const legs = tripData.route.legs || [];

                // Add markers for each waypoint
                legs.forEach((leg, index) => {
                    if (index < legs.length - 1) { // Skip the last leg (destination)
                        // Use the end address of each leg as a waypoint
                        const waypointAddress = leg.end_address;

                        // Find the corresponding coordinates for this waypoint
                        // We will use the end coordinates of each leg
                        const waypointCoordinates = routeCoordinates.find((coord, i) => {
                            // This is a simplified approach - in a real app, you would want to use geocoding
                            // to get the exact coordinates for each waypoint
                            return i > 0 && i < routeCoordinates.length - 1;
                        });

                        if (waypointCoordinates) {
                            newMarkers.push({
                                position: waypointCoordinates,
                                type: "waypoint",
                                info: `<b>WayPoint:</b> ${waypointAddress}`
                            });
                        }
                    }
                });
            }

            // Add weather markers if available
            // if (tripData.weather && Array.isArray(tripData.weather)) {
            //     tripData.weather.forEach((weather, index) => {
            //         if (weather && weather.coords && Array.isArray(weather.coords) && weather.coords.length >= 2) {
            //             newMarkers.push({
            //                 position: weather.coords,
            //                 type: "weather",
            //                 info: `<b>Weather:</b> ${weather.condition || "Unknown"}<br />
            //                     <b>Temperature:,/b> ${weather.temperature || "N/A"}<br />
            //                     <b>Precipitation:</b> ${weather.precipitation || "N/A"}%`
            //             });
            //         }
            //     });
            // }

            // Add traffic markers if available
            // if (tripData.traffic && tripData.traffic.incidents && Array.isArray(tripData.traffic.incidents)) {
            //     tripData.traffic.incidents.forEach((incident, index) => {
            //         if (incident && incident.coords && Array.isArray(incident.coords) && incident.coords.length >= 2) {
            //             newMarkers.push({
            //                 position: incident.coords,
            //                 type: "traffic",
            //                 info: `<b>Traffic Incident:</b> ${incident.description || "Unknown"}<br />
            //                     <b>Severity:</b> ${incident.severity || "N/A"}<br />
            //                     <b>Delay:</b> ${incident.delay || "N/A"} minutes`
            //             });
            //         }
            //     });
            // }

            // Add recommendation markers if available
            // if (tripData.recommendations && Array.isArray(tripData.recommendations)) {
            //     tripData.recommendations.forEach((recommendation) => {
            //         if (recommendation && recommendation.coords && Array.isArray(recommendation.coords) && recommendation.coords.length >= 2) {
            //             // Add recommendation marker
            //             newMarkers.push({
            //                 position:  recommendation.coords,
            //                 type: "recommendation",
            //                 info: `<b>${recommendation.name || "Attraction"}</b><br />
            //                     <b>Type:</b> ${recommendation.type || "Unknown"}<br />
            //                     <b>Address:</b> ${recommendation.address || "N/A"}<br />
            //                     <b>Phone:</b> ${recommendation.phone_number || "N/A"}<br />
            //                     <b>Rating:</b> ${recommendation.rating || "N/A"}<br />
            //                     <b>Description:</b> ${recommendation.description || "No description available"}`
            //             })
            //         }
            //     })
            // }

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
                                        // console.log("Added recommendation marker:", {
                                        //     subtype: category,
                                        //     name: item.name,
                                        //     coords: item.coords
                                        // });
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
            // Create route segments based on traffic data if available
            if (tripData.traffic && tripData.traffic.segments && tripData.traffic.segments.length > 0) {
                const segments = [];

                // Process each traffic segment
                tripData.traffic.segments.forEach((segment, index) => {
                    if (segment && segment.coordinates && Array.isArray(segment.coordinates) && segment.coordinates.length > 0) {
                        // Determine color based on congestion level
                        let color = "#4CAF50"; // default Green
                        if (segment.congestion_level === "moderate") {
                            color = "#FFC107"; // Yellow
                        } else if (segment.congestion_level === "heavy") {
                            color = "#F44336"; // Red
                        } else if (segment.congestion_level === "unknown") {
                            color = "#9E9E9E"; // Grey
                        }

                        segments.push({
                            positions: segment.coordinates,
                            color: color
                        });
                    }
                });

                // If we have segments, use them
                if (segments.length > 0) {
                    setRouteSegments(segments);
                } else {
                    // Fallback to a single segment for the entire route
                    setRouteSegments([{
                        positions: routeCoordinates,
                        color: "#4CAF50" // Green for the route
                    }]);
                }
            } else {
                // Create a single route segment for the entire route
                setRouteSegments([{
                    positions: routeCoordinates,
                    color: "#4CAF50" // Green for the route
                }]);
            }

            // Add traffic markers
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

            // // Add weather markers
            // if (tripData.weather) {
            //     Object.entries(tripData.weather).forEach(([location, data]) => {
            //         if (data && data.coords) {
            //             newMarkers.push({
            //                 position: data.coords,
            //                 type: "weather",
            //                 info: `${data.condition}, ${data.temperature}`
            //             });
            //         }
            //     });
            // } else {
            //     console.warn("No valid weather data found.");
            // }

            setMarkers(newMarkers);
            const renderEnd = performance.now();
        }
        catch (error) {
            console.error("Error processing route coordinates:", error);
        }
    }, [tripData]);

    // Function to get the appropriate icon based on marker type
    const getMarkerIcon = (type) => {
        switch (type) {
            case "origin":
                return originIcon;
            case "destination":
                return destinationIcon;
            case "waypoint":
                return waypointIcon;
            case "weather":
                return weatherIcon;
            case "traffic":
                return trafficIcon;
            case "recommendation":
                return recommendationIcon;
            default:
                return waypointIcon;
        }
    };

    return (
        <MapContainer
            center={center}
            zoom={6}
            style={{ height: "100vh", width: "100%" }}
            bounds={mapBounds}
            boundsOptions={{ padding: [50, 50] }}
        >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

            {/* Route Polyline */}
            {route.length > 1 && <Polyline positions={route} color="blue" />}

            {markers.map((marker, index) => (
                <Marker
                key={index}
                position={marker.position}
                icon={marker.type === "weather" 
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
    )
};

export default MapView;