import { useState, useEffect, useRef } from 'react';
import './AddressSearch.css';

export default function AddressSearch({ onAddressSelect }) {
    const [query, setQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [selectedAddress, setSelectedAddress] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const suggestionListRef = useRef(null);
    
  // Replace with your actual Mapbox access token
  const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYW1pc2hyMTAiLCJhIjoiY205ZXJ2ODF3MWdnbDJsb2RwdzNmMndpdSJ9.zb8gsQWOvKV-AThsntpO7g';

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 3) {
        setSuggestions([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const endpoint = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(
          query
        )}.json?access_token=${MAPBOX_ACCESS_TOKEN}&autocomplete=true&types=address`;

        const response = await fetch(endpoint);
        
        if (!response.ok) {
          throw new Error('Failed to fetch address suggestions');
        }

        const data = await response.json();
        setSuggestions(data.features || []);
      } catch (err) {
        console.error('Error fetching address suggestions:', err);
        setError('Failed to load address suggestions. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce the API calls
    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelectAddress = (suggestion) => {
    setSelectedAddress(suggestion.place_name);
    setQuery(suggestion.place_name);
    setSuggestions([]);
    if (onAddressSelect){
        onAddressSelect(suggestion.place_name);
    }
  };

  // Handle clicking outside the suggestions list to close it
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionListRef.current && !suggestionListRef.current.contains(event.target)) {
        setSuggestions([]);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="w-full max-w-lg mx-auto">
      {/*<label htmlFor="Pharmacy Address" className="block text-sm font-medium text-gray-700 mb-1">
        Pharmacy Address
      </label>*/}
      
      <div className="w-full relative flex justify-center">
        <input
          type="text"
          id="address"
          name="address"
          //className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          className='w-full py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition'
          placeholder="Start typing an address..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-autocomplete="list"
          aria-controls="suggestions-list"
          aria-expanded={suggestions.length > 0}
          required
        />
        
        {isLoading && (
          <div className="absolute right-3 top-2">
            <div className="animate-spin h-5 w-5 border-2 border-gray-500 rounded-full border-t-transparent"></div>
          </div>
        )}
        
        {suggestions.length > 0 && (
          <ul 
            id="suggestions-list"
            ref={suggestionListRef}
            //style={{ top: 'calc(100% + 8px)' }}
            //className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md overflow-auto border border-gray-300 py-1 list-none p-0"
            className="absolute z-10 top-full mt-1 sm:mt-2 md:mt-3 w-full bg-white shadow-lg max-h-60 rounded-md overflow-auto border border-gray-300 py-1 list-none p-0"
            role="listbox"
          >
            {suggestions.map((suggestion) => (
              <li
                key={suggestion.id}
                //className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                className={`mx-1 my-1 px-4 py-3 rounded cursor-pointer transition-colors 
                  ${selectedAddress === suggestion.place_name 
                    ? 'bg-blue-50 border border-blue-300' 
                    : 'hover:bg-gray-100 border border-transparent hover:border-gray-200'
                  }`}
                onClick={() => handleSelectAddress(suggestion)}
                role="option"
                aria-selected={selectedAddress === suggestion.place_name}
              >
                <div className="flex items-start">
                  {/* CHANGE 5: Added map pin icon */}
                  <div className="flex-shrink-0 text-gray-500 mr-2">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 21C16 17 20 13.4183 20 9C20 4.58172 16.4183 1 12 1C7.58172 1 4 4.58172 4 9C4 13.4183 8 17 12 21Z" 
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M12 12C13.6569 12 15 10.6569 15 9C15 7.34315 13.6569 6 12 6C10.3431 6 9 7.34315 9 9C9 10.6569 10.3431 12 12 12Z" 
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{suggestion.address + " " + suggestion.text}</div>
                    <div className="text-xs text-gray-500 mt-1 truncate">{suggestion.place_name.replace(suggestion.address + " " + suggestion.text + ', ', '')}</div>
                  </div>
                </div>
                {/*{suggestion.place_name}*/}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      
      {/*{selectedAddress && (
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <h3 className="text-sm font-medium text-gray-700">Selected Address:</h3>
          <p className="mt-1 text-sm text-gray-900">{selectedAddress}</p>
        </div>
      )}*/}
    </div>
  );
}
