import React, { useState, useEffect } from 'react';
import './NonProfit.css'; // styling goes here

/*
function NonProfit() {
    return (
      <main className="nonprofit-container">
        <div className="nonprofit-card">
          <h1 className="nonprofit-title">Search For Available Medicine</h1>
          <form className="nonprofit-form">
            <input
              type="text"
              placeholder="Type a medicine name"
              aria-label="Search medicine"
              className="nonprofit-input"
            />
            <button type="submit" className="nonprofit-button">
              Search
            </button>
          </form>
        </div>
      </main>
    );
  }
  
  export default NonProfit;
  */
  function NonProfit() {
    const [query, setQuery] = useState('');
    const [formError, setFormError] = useState('');
    const [results, setResults] = useState(null);
  
    // Restore last search from localStorage (optional UX touch)
    useEffect(() => {
      const saved = localStorage.getItem('lastSearch');
      if (saved) setQuery(saved);
    }, []);
  
    const handleChange = (e) => {
      setQuery(e.target.value);
      setFormError('');
    };
  
    const handleSubmit = (e) => {
      e.preventDefault();
  
      if (!query.trim()) {
        setFormError('Please enter a valid medicine name.');
        return;
      }
  
      // Example logic (replace with real API call if needed)
      localStorage.setItem('lastSearch', query);
      setResults(`You searched for "${query}"`);
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
              {formError && (
                <p className="text-red-600 text-sm mt-2">{formError}</p>
              )}
            </div>
  
            <button type="submit" className="nonprofit-button">
              Search
            </button>
          </form>
  
          {results && (
            <p className="text-center mt-4 text-sm text-gray-700">
              {results}
            </p>
          )}
        </div>
      </main>
    );
  }
  
  export default NonProfit;