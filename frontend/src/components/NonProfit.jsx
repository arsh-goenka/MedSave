import React, { useState, useEffect } from 'react';
import './NonProfit.css'; 
import AddressSearch from './AddressSearch';

function haversine(coord1, coord2) {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 6371; // Earth radius in kilometers

  const dLat = toRad(coord2.lat - coord1.lat);
  const dLon = toRad(coord2.lng - coord1.lng);
  const lat1 = toRad(coord1.lat);
  const lat2 = toRad(coord2.lat);

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.sin(dLon / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function NonProfit() {
  const [query, setQuery] = useState('');
  const [userAddress, setUserAddress] = useState('');
  const [userCoordinates, setUserCoordinates] = useState(null);
  const [formError, setFormError] = useState('');
  const [results, setResults] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      (error) => console.error('Error getting user location:', error),
      { enableHighAccuracy: true }
    );
  }, []);

  const handleChange = async (e) => {
    setQuery(e.target.value);
    setFormError('');
  };

  const handleAddressSelect = (selectedAddress) => {
    setUserAddress(selectedAddress);
    setFormError('');
  };

  const handleSubmit = async (e) => { 
    e.preventDefault();

    if (!query.trim()) {
      setFormError('Please enter a valid medicine name.');
      return;
    }
    
    if (!userAddress.trim()) {
      setFormError('Please enter your address.');
      return;
    }
    
    try {
      // Replace with your actual Mapbox token
      const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYW1pc2hyMTAiLCJhIjoiY205ZXJ2ODF3MWdnbDJsb2RwdzNmMndpdSJ9.zb8gsQWOvKV-AThsntpO7g';
      
      console.log(`Attempting to geocode address: ${userAddress}`);
      
      const addressRes = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(userAddress)}.json?access_token=${MAPBOX_ACCESS_TOKEN}`
      );
      
      console.log('Geocode response status:', addressRes.status);
      
      if (!addressRes.ok) {
        const errorText = await addressRes.text();
        console.error('Geocode error response:', errorText);
        throw new Error(`Failed to geocode your address: ${addressRes.status} - ${errorText}`);
      }
      
      const addressData = await addressRes.json();
      console.log('Geocode response data:', addressData);
      
      if (!addressData.features || addressData.features.length === 0) {
        throw new Error('Unable to locate your address.');
      }
      
      const userCoords = addressData.features[0]?.geometry.coordinates;

      if (!userCoords) throw new Error('Unable to locate your address.');

      const userLoc = { lng: userCoords[0], lat: userCoords[1] };
      setUserCoordinates(userLoc);

      const res = await fetch(`http://127.0.0.1:5000/medicines/query?name=${encodeURIComponent(query)}`);
      
      if (!res.ok) throw new Error(`Error fetching medicine data: ${res.status} ${res.statusText}`);

      const data = await res.json();
      
      if (!Array.isArray(data) || data.length === 0) {
        setResults([]);
        setFormError('No medicines found matching your criteria.');
        return;
      }

      // Calculate distances as part of geocoding the pharmacy addresses
      const geocodedResults = await Promise.all(
        data.map(async (med) => {
          try {
            const geoRes = await fetch(
              `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(med.address)}.json?access_token=${MAPBOX_ACCESS_TOKEN}`
            );
            
            if (!geoRes.ok) {
              throw new Error(`Failed to geocode pharmacy address: ${geoRes.status}`);
            }
            
            const geoData = await geoRes.json();
            
            if (!geoData.features || geoData.features.length === 0) {
              return {
                ...med,
                longitude: null,
                latitude: null,
                distance: null
              };
            }
            
            const coords = geoData.features[0]?.geometry.coordinates;
            
            // Calculate distance if we have both user and pharmacy coordinates
            let distance = null;
            if (coords && userLoc) {
              const pharmacyLoc = { lat: coords[1], lng: coords[0] };
              distance = haversine(userLoc, pharmacyLoc);
            }
            
            return {
              ...med,
              longitude: coords?.[0],
              latitude: coords?.[1],
              distance: distance
            };
          } catch (err) {
            console.error('Error geocoding pharmacy:', med.address, err);
            return {
              ...med,
              longitude: null,
              latitude: null,
              distance: null
            };
          }
        })  
      );


      const filtered = geocodedResults.filter((m) => 
        m.latitude !== null && 
        m.longitude !== null && 
        m.distance !== null
      );
      

      const noDistanceInfo = geocodedResults.filter((m) => 
        m.latitude === null || 
        m.longitude === null || 
        m.distance === null
      );
      
      let sorted = [];
      
      if (filtered.length > 0) {

        sorted = [...filtered].sort((a, b) => {
          // We know these are numbers since we filtered for non-null values
          return a.distance - b.distance;
        });
        

        sorted = [...sorted, ...noDistanceInfo];
      } else {
        sorted = geocodedResults;
      }
      

      console.log('Sorted results:', sorted);

      setResults(sorted);
      setFormError('');
    } catch (err) {
      console.error('Search error:', err);
      setFormError(`Error: ${err.message || 'Could not complete the search. Please check your inputs.'}`);
      setResults(null);
    }
  };

  const formatDistance = (distance) => {
    if (distance === null || distance === undefined) {
      return 'Unknown';
    }
    
    // Convert from km to miles if needed
    const miles = distance * 0.621371;
    
    if (miles < 0.1) {
      return 'Less than 0.1 mi';
    } else {
      return `${miles.toFixed(1)} mi`;
    }
  };

  return (
    <main className="nonprofit-container">
      <div className="nonprofit-card search-box">
        <form className="nonprofit-form" onSubmit={handleSubmit} aria-label="Medicine Search Form">
          <h1 className="nonprofit-title">Search For Available Medicine</h1>

          <div className="form-group">
            <label htmlFor="medicine-search" className="sr-only">Medicine Name</label>
            <input
              id="medicine-search"
              type="text"
              placeholder="e.g. Ibuprofen"
              aria-label="Search medicine"
              value={query}
              onChange={handleChange}
              className={`nonprofit-input ${formError ? 'input-error' : ''}`}
              required
            />
          </div>

          <div className="form-group">
            <AddressSearch onAddressSelect={handleAddressSelect}/>
          </div>

          {formError && (
            <p className="text-red-600 text-sm mt-2">{formError}</p>
          )}
        
          <button type="submit" className="nonprofit-button">
            Search
          </button>
        </form>
        
        {Array.isArray(results) && results.length === 0 && (
          <div className="no-results">
            <p>No pharmacies found with the requested medicine.</p>
          </div>
        )}
        
        {Array.isArray(results) && results.length > 0 && (
          <div className="search-results">
            <table className="results-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Pharmacy</th>
                  <th>Location</th>
                  <th>Price ($)</th>
                  <th>Quantity</th>
                  <th>Distance</th>
                </tr>
              </thead>
              <tbody>
                {results.map((med, idx) => (
                  <tr key={idx}>
                    <td>{med.generic_name}</td>
                    <td>{med.pharmacy_name}</td>
                    <td>{med.address}</td>
                    <td>{med.price}</td>
                    <td>{med.quantity}</td>
                    <td>{formatDistance(med.distance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}

export default NonProfit;