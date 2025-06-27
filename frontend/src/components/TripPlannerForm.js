import React, { useState } from 'react';
import './TripPlannerForm.css';

const ATTRACTION_TYPES = [
    { id: 'amusement_park', label: 'Amusement Park' },
    { id: 'aquarium', label: 'Aquarium' },
    { id: 'art_gallery', label: 'Art Gallery' },
    { id: 'beach', label: 'Beach'},
    { id: 'casino', label: 'Casino' },
    { id: 'cultural_landmark', label: 'Cultural Landmark'},
    { id: 'electric_vehicle_charging_station', label: 'Charging Station'},
    { id: 'gas_station', label: 'Gas Station'},
    { id: 'historical_landmark', label: 'Historical Landmark'},
    { id: 'movie_theater', label: 'Movie Theater' },
    { id: 'museum', label: 'Museum' },
    { id: 'night_club', label: 'Night Club' },
    { id: 'park', label: 'Park' },
    { id: 'rest_stop', label: 'Rest Stop'},
    { id: 'stadium', label: 'Stadium' },
    { id: 'theme_park', label: 'Theme Park' },
    { id: 'tourist_attraction', label: 'Tourist Attraction' },
    { id: 'zoo', label: 'Zoo' }
];

const TripPlannerForm = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
        origin: '',
        destination: '',
        waypoints: [''],
        departureTime: '',
        stopDurations: [''],
        attractionPreferences: []
    });
    const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = (e, index) => 
    {
        const { name, value } = e.target;

        if (name === 'waypoints' || name === 'stopDurations') 
        {
            const newValues = [...formData[name]];
            newValues[index] = value;
            setFormData(prev => ({
                ...prev,
                [name]: newValues
            }));
        } 
        else 
        {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const handleAddWaypoint = () => {
        setFormData(prev => ({
            ...prev,
            waypoints: [...prev.waypoints, ''],
            stopDurations: [...prev.stopDurations, '']
        }));
    };

    const handleRemoveWaypoint = (index) => {
        setFormData(prev => ({
            ...prev,
            waypoints: prev.waypoints.filter((_, i) => i !== index),
            stopDurations: prev.stopDurations.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try 
        {
            setIsLoading(true);
            setIsLoading(true);
            // Convert stopDurations to numbers
            const stopDurations = formData.stopDurations.map(duration => 
                duration ? parseInt(duration) : 0
            );

            // Filter out empty waypoints
            const waypoints = formData.waypoints.filter(wp => wp && wp.trim() !== '');

            await onSubmit({
                ...formData,
                waypoints,
                stopDurations,
                attractionPreferences: formData.attractionPreferences || []
            });
        } 
        catch (error) 
        {
            console.error('Error in form submission:', error);
        } 
        finally 
        {
            setIsLoading(false);
        }
    };

    const handlePreferenceChange = (pref, checked) => 
    {
        const newPreferences = checked
            ? [...(formData.attractionPreferences || []), pref]
            : (formData.attractionPreferences || []).filter(p => p !== pref);
        setFormData(prev => ({
            ...prev,
            attractionPreferences: newPreferences
        }));
    };

    // Helper function to capitalize first letter
    const capitalizeFirstLetter = (str) => 
    {
        if (!str || typeof str !== 'string') return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    };

    return (
        <div>
            <h1 className="page-header">Your Journey Awaits</h1>
            <form onSubmit={handleSubmit} className="trip-planner-form">
                <div className="form-group">
                    <label>Origin:</label>
                    <input
                        type="text"
                        name="origin"
                        value={formData.origin || ''}
                        onChange={handleInputChange}
                        required
                        placeholder="Enter starting location"
                    />
                </div>

                <div className="form-group">
                    <label>Destination:</label>
                    <input
                        type="text"
                        name="destination"
                        value={formData.destination || ''}
                        onChange={handleInputChange}
                        required
                        placeholder="Enter destination"
                    />
                </div>

                <div className="form-section">
                    <h3>Waypoints</h3>
                    {formData.waypoints.map((waypoint, index) => (
                        <div key={index} className="waypoint-group">
                            <div className="waypoint-input-group">
                                <label htmlFor={`waypoint-${index}`}>Stop {index + 1}</label>
                                <input
                                    type="text"
                                    id={`waypoint-${index}`}
                                    name="waypoints"
                                    value={waypoint}
                                    onChange={(e) => handleInputChange(e, index)}
                                    placeholder="Enter city name"
                                    required
                                />
                            </div>
                            <div className="duration-input-group">
                                <label htmlFor={`duration-${index}`}>Stop Duration (hours)</label>
                                <input
                                    type="number"
                                    id={`duration-${index}`}
                                    name="stopDurations"
                                    value={formData.stopDurations[index] || ''}
                                    onChange={(e) => handleInputChange(e, index)}
                                    min="1"
                                    max="24"
                                    required
                                />
                            </div>
                            <button
                                type="button"
                                onClick={() => handleRemoveWaypoint(index)}
                                className="remove-waypoint-btn"
                            >
                                Remove
                            </button>
                        </div>
                    ))}
                    <button type="button" onClick={handleAddWaypoint} className="add-waypoint-btn">
                        Add Waypoint
                    </button>
                </div>

                <div className="form-group">
                    <label>Departure Time:</label>
                    <input
                        type="datetime-local"
                        name="departureTime"
                        value={formData.departureTime || ''}
                        onChange={handleInputChange}
                        required
                    />
                </div>

                <div className="form-section">
                    <h3>Attraction Preferences</h3>
                    <div className="preference-grid">
                        {ATTRACTION_TYPES.map((type) => (
                            <div key={type.id} className="preference-checkbox">
                                <input
                                    type="checkbox"
                                    id={type.id}
                                    checked={formData.attractionPreferences.includes(type.id)}
                                    onChange={(e) => handlePreferenceChange(type.id, e.target.checked)}
                                />
                                <label htmlFor={type.id}>{type.label}</label>
                            </div>
                        ))}
                    </div>
                </div>

                <button 
                    type="submit" 
                    className="submit-button"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <div className="loading-indicator">
                            <div className="loading-spinner"></div>
                            Planning your trip...
                        </div>
                    ) : (
                        'Plan Trip'
                    )}
                </button>
            </form>
        </div>
    );
};

export default TripPlannerForm; 