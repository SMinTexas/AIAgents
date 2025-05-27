import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker icons
const markerIcons = {
    origin: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #4CAF50; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    destination: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #F44336; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    waypoint: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #2196F3; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    weather: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #FFC107; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    traffic: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #FF9800; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    // Attraction type markers
    museum: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #9C27B0; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    shopping: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #E91E63; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    festival: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #03A9F4; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    tourist_attraction: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #3F51B5; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    zoo: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #4CAF50; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    casino: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #F44336; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    aquarium: L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: #00BCD4; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    })
};

// Google Place Icon URLs and background colors for categories
const PLACE_TYPE_ICON_INFO = {
    restaurant: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet.svg",
        color: "#FF7043"
    },
    shopping_mall: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/shopping_pinlet.svg",
        color: "#AB47BC"
    },
    lodging: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/lodging_pinlet.svg",
        color: "#29B6F6"
    },
    museum: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/museum_pinlet.svg",
        color: "#8D6E63"
    },
    park: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/park_pinlet.svg",
        color: "#66BB6A"
    },
    stadium: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/stadium_pinlet.svg",
        color: "#FFA726"
    },
    zoo: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/zoo_pinlet.svg",
        color: "#26A69A"
    },
    aquarium: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/aquarium_pinlet.svg",
        color: "#42A5F5"
    },
    casino: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/casino_pinlet.svg",
        color: "#EC407A"
    },
    art_gallery: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/art_gallery_pinlet.svg",
        color: "#7E57C2"
    },
    bowling_alley: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bowling_alley_pinlet.svg",
        color: "#FFB300"
    },
    movie_theater: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/movie_theater_pinlet.svg",
        color: "#78909C"
    },
    night_club: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/night_club_pinlet.svg",
        color: "#D4E157"
    },
    tourist_attraction: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/tourist_attraction_pinlet.svg",
        color: "#26C6DA"
    },
    default: {
        icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet.svg",
        color: "#BDBDBD"
    }
};

// Helper to get icon info for a place type
const getPlaceIconInfo = (type) => {
    return PLACE_TYPE_ICON_INFO[type] || PLACE_TYPE_ICON_INFO.default;
};

// Helper to create a Leaflet divIcon with a Google icon and background color
const createPlaceDivIcon = (type) => {
    const { icon, color } = getPlaceIconInfo(type);
    return L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${color}; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><img src='${icon}' style='width: 20px; height: 20px; display: block; margin: auto;'/></div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });
};

const MapView = ({ tripData }) => {
    // Default center coordinates (will be updated when route data is available)
    const defaultCenter = [39.8283, -98.5795]; // Center of USA
    const [route, setRoute] = useState([]);
    const [center, setCenter] = useState(defaultCenter);
    const [markers, setMarkers] = useState([]);
    const [routeSegments, setRouteSegments] = useState([]);
    const [mapBounds, setMapBounds] = useState(null);

    useEffect(() => {
        // Reset state when tripData changes
        setRoute([]);
        setMarkers([]);
        setRouteSegments([]);
        setCenter(defaultCenter);
        setMapBounds(null);

        // Early return if no valid data
        if (!tripData || !tripData.route || !tripData.route.coordinates || !Array.isArray(tripData.route.coordinates) || tripData.route.coordinates.length === 0) {
            console.warn("No valid route data available");
            return;
        }

        try {
            console.log("Processing tripData:", tripData);
            
            // Safely extract coordinates
            const routeCoordinates = tripData.route.coordinates
                .filter(coord => Array.isArray(coord) && coord.length >= 2)
                .map(coord => [coord[0], coord[1]]);

            if (routeCoordinates.length === 0) 
            {
                console.warn("No valid route coordinates after filtering");
                return;
            }

            // console.log("Route coordinates:", routeCoordinates);
            // console.log("First coordinate:", routeCoordinates[0]);
            // console.log("Last coordinate:", routeCoordinates[routeCoordinates.length - 1]);

            // Get the destination coordinates from the route data or use the last coordinate
            const destinationCoords = tripData.route.destination_coords || routeCoordinates[routeCoordinates.length - 1];
            // console.log("Destination coordinates:", destinationCoords);

            // Use the route coordinates as is
            setRoute(routeCoordinates);
            
            // Set map center to origin (first coordinate of the route)
            setCenter(routeCoordinates[0]);

            // Create a bounds object to fit all markers
            const bounds = L.latLngBounds(routeCoordinates);
            setMapBounds(bounds);

            // Add origin and destination markers
            const newMarkers = [
                {
                    position: routeCoordinates[0],
                    type: "origin",
                    info: "Starting Point"
                },
                {
                    position: destinationCoords,
                    type: "destination",
                    info: "Destination Point"
                }
            ];

            // Add waypoint markers if available
            if (tripData.route.waypoints && Array.isArray(tripData.route.waypoints) && tripData.route.waypoints.length > 0) 
            {
                console.log("Processing waypoints:", tripData.route.waypoints);
                
                // Get the legs from the route data
                const legs = tripData.route.legs || [];
                console.log("Route legs:", legs);
                
                // Add markers for each waypoint
                legs.forEach((leg, index) => 
                {
                    if (index < legs.length - 1) 
                    { // Skip the last leg (destination)
                        // Use the end address of each leg as a waypoint
                        const waypointAddress = leg.end_address;
                        console.log(`Processing leg ${index} with end address: ${waypointAddress}`);
                        
                        // Find the corresponding coordinates for this waypoint
                        // We'll use the end coordinates of each leg
                        const waypointCoords = leg.end_location || routeCoordinates.find((coord, i) => {
                            // This is a simplified approach - in a real app, you might want to use geocoding
                            // to get the exact coordinates for each waypoint
                            return i > 0 && i < routeCoordinates.length - 1;
                        });
                        
                        if (waypointCoords) 
                        {
                            console.log(`Adding waypoint marker at ${waypointCoords} for ${waypointAddress}`);
                            newMarkers.push({
                                position: waypointCoords,
                                type: "waypoint",
                                info: `<b>Waypoint:</b> ${waypointAddress}`
                            });
                        } 
                        else 
                        {
                            console.warn(`Could not find coordinates for waypoint: ${waypointAddress}`);
                        }
                    }
                });
            }

            // Add route attractions if available
            if (tripData.route.route_attractions && Array.isArray(tripData.route.route_attractions)) 
            {
                console.log("Processing route attractions:", tripData.route.route_attractions);
                
                tripData.route.route_attractions.forEach(attraction => 
                    {
                    if (attraction.location) 
                    {
                        newMarkers.push({
                            position: [attraction.location.lat, attraction.location.lng],
                            type: "attraction",
                            info: `
                                <b>${attraction.name}</b><br>
                                Type: ${attraction.type}<br>
                                Rating: ${attraction.rating}<br>
                                Distance from route: ${Math.round(attraction.distance_from_route)}m
                            `
                        });
                    }
                });
            }

            // Add weather markers if available
            if (tripData.weather && typeof tripData.weather === 'object') 
            {
                console.log("Processing weather data:", tripData.weather);
                
                // Convert weather object to array of entries
                const weatherEntries = Object.entries(tripData.weather);
                
                weatherEntries.forEach(([location, weather]) => {
                    if (weather && weather.coords) {
                        newMarkers.push({
                            position: weather.coords,
                            type: "weather",
                            info: `
                                <b>${location}</b><br>
                                Temperature: ${weather.temperature}<br>
                                Condition: ${weather.condition}
                            `
                        });
                    }
                });
            }

            // Add traffic markers if available
            if (tripData.traffic && tripData.traffic.incidents && Array.isArray(tripData.traffic.incidents)) 
            {
                console.log("Processing traffic incidents:", tripData.traffic.incidents);
                
                tripData.traffic.incidents.forEach((incident, index) => 
                {
                    if (incident && incident.coords && Array.isArray(incident.coords) && incident.coords.length >= 2) 
                    {
                        console.log(`Adding traffic incident marker at ${incident.coords}`);
                        
                        newMarkers.push({
                            position: incident.coords,
                            type: "traffic",
                            info: `<b>Traffic Incident:</b> ${incident.description || "Unknown"}<br />
                                <b>Severity:</b> ${incident.severity || "N/A"}<br />
                                <b>Delay:</b> ${incident.delay || "N/A"} minutes`
                        });
                    }
                });
            }

            // Add recommendation markers if available
            if (tripData.recommendations && typeof tripData.recommendations === 'object') 
            {
                console.log("Processing recommendations:", tripData.recommendations);
                
                // Process each location's recommendations
                Object.entries(tripData.recommendations).forEach(([location, locationData]) => 
                {
                    console.log(`Processing recommendations for ${location}:`, locationData);
                    
                    // Process hotels (limit to 5)
                    if (locationData.hotels && Array.isArray(locationData.hotels)) 
                    {
                        const hotels = locationData.hotels.slice(0, 5);
                        console.log(`Adding ${hotels.length} hotel markers for ${location}`);
                        
                        hotels.forEach((hotel, index) => 
                        {
                            if (hotel && hotel.geometry && hotel.geometry.location) 
                            {
                                const coords = [hotel.geometry.location.lat, hotel.geometry.location.lng];
                                console.log(`Adding hotel marker at ${coords} for ${hotel.name}`);
                                
                                newMarkers.push({
                                    position: coords,
                                    type: "hotel",
                                    info: `<b>Hotel:</b> ${hotel.name || "Unknown"}<br />
                                        <b>Rating:</b> ${hotel.rating || "N/A"}<br />
                                        <b>Address:</b> ${hotel.vicinity || "N/A"}`
                                });
                            }
                        });
                    }
                    
                    // Process restaurants (limit to 5)
                    if (locationData.restaurants && Array.isArray(locationData.restaurants)) 
                    {
                        const restaurants = locationData.restaurants.slice(0, 5);
                        console.log(`Adding ${restaurants.length} restaurant markers for ${location}`);
                        
                        restaurants.forEach((restaurant, index) => 
                        {
                            if (restaurant && restaurant.geometry && restaurant.geometry.location) 
                            {
                                const coords = [restaurant.geometry.location.lat, restaurant.geometry.location.lng];
                                console.log(`Adding restaurant marker at ${coords} for ${restaurant.name}`);
                                
                                newMarkers.push({
                                    position: coords,
                                    type: "restaurant",
                                    info: `<b>Restaurant:</b> ${restaurant.name || "Unknown"}<br />
                                        <b>Rating:</b> ${restaurant.rating || "N/A"}<br />
                                        <b>Address:</b> ${restaurant.vicinity || "N/A"}`
                                });
                            }
                        });
                    }
                    
                    // Process attractions (limit to 5)
                    if (locationData.attractions && Array.isArray(locationData.attractions)) 
                    {
                        const attractions = locationData.attractions.slice(0, 5);
                        console.log(`Adding ${attractions.length} attraction markers for ${location}`);
                        
                        attractions.forEach((attraction, index) => {
                            if (attraction && attraction.geometry && attraction.geometry.location) 
                            {
                                const coords = [attraction.geometry.location.lat, attraction.geometry.location.lng];
                                console.log(`Adding attraction marker at ${coords} for ${attraction.name}`);
                                
                                newMarkers.push({
                                    position: coords,
                                    type: "attraction",
                                    info: `<b>Attraction:</b> ${attraction.name || "Unknown"}<br />
                                        <b>Rating:</b> ${attraction.rating || "N/A"}<br />
                                        <b>Address:</b> ${attraction.vicinity || "N/A"}`
                                });
                            }
                        });
                    }
                });
            } else 
            {
                console.warn("No valid recommendations data available");
            }

            // Create route segments based on traffic data if available
            if (tripData.traffic && tripData.traffic.segments && tripData.traffic.segments.length > 0) 
            {
                console.log("Processing traffic segments:", tripData.traffic.segments);
                
                const segments = [];
                
                // Process each traffic segment
                tripData.traffic.segments.forEach((segment, index) => 
                {
                    if (segment && segment.coordinates && Array.isArray(segment.coordinates) && segment.coordinates.length > 0) 
                    {
                        // Determine color based on congestion level
                        let color = "#4CAF50"; // Default green
                        if (segment.congestion_level === "moderate") 
                        {
                            color = "#FFC107"; // Yellow
                        } else if (segment.congestion_level === "heavy") 
                        {
                            color = "#F44336"; // Red
                        } else if (segment.congestion_level === "unknown") 
                        {
                            color = "#9E9E9E"; // Grey
                        }
                        
                        segments.push({
                            positions: segment.coordinates,
                            color: color
                        });
                    }
                });
                
                // If we have segments, use them
                if (segments.length > 0) 
                {
                    setRouteSegments(segments);
                } else 
                {
                    // Fallback to a single segment for the entire route
                    setRouteSegments([{
                        positions: routeCoordinates,
                        color: "#4CAF50" // Green color for the route
                    }]);
                }
            } 
            else 
            {
                // Create a single route segment for the entire route
                setRouteSegments([{
                    positions: routeCoordinates,
                    color: "#4CAF50" // Green color for the route
                }]);
            }

            console.log("Setting markers:", newMarkers);
            setMarkers(newMarkers);
        } 
        catch (error) 
        {
            console.error("Error processing route coordinates:", error);
        }
    }, [tripData]);

    // Function to get the appropriate icon based on marker type
    const getMarkerIcon = (type) => {
        // Use Google Place icons for known place types
        if (PLACE_TYPE_ICON_INFO[type]) {
            return createPlaceDivIcon(type);
        }
        // Fallback to previous icons for origin, destination, etc.
        switch (type) {
            case "origin":
                return markerIcons.origin;
            case "destination":
                return markerIcons.destination;
            case "waypoint":
                return markerIcons.waypoint;
            case "weather":
                return markerIcons.weather;
            case "traffic":
                return markerIcons.traffic;
            default:
                return createPlaceDivIcon("default");
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
            
            {/* Route segments */}
            {routeSegments && routeSegments.length > 0 && routeSegments.map((segment, index) => (
                <Polyline
                    key={index}
                    positions={segment.positions}
                    color={segment.color}
                    weight={6}
                    opacity={0.7}
                />
            ))}

            {/* Markers for waypoints and recommendations */}
            {markers && markers.length > 0 && markers.map((marker, index) => (
                <Marker
                    key={index}
                    position={marker.position}
                    icon={getMarkerIcon(marker.type)}
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
