import React, { useState, useEffect } from 'react';
import './NonProfit.css'; // styling goes here
  function NonProfit() {
    const [query, setQuery] = useState('');
    const [formError, setFormError] = useState('');
    const [results, setResults] = useState(null);
    
    
    // Save last search to localStorage (optional UX touch)
    const handleChange = async (e) => {
      setQuery(e.target.value);
      setFormError('');
    };
  
    const handleSubmit = async (e) => { 
      e.preventDefault();
  
      if (!query.trim()) {
        setFormError('Please enter a valid medicine name.');
        return;
      }
      try{
        const res = await fetch(`http://127.0.0.1:5000/medicines/query?name=${query}`);
        if (!res.ok) throw new Error('No results found');

        const data = await res.json();
        setResults(data);
        setFormError('');
    } catch (err) {
        console.error(err);
        setFormError('Could not find that medicine.');
        setResults(null);
    }
      
    };
    //button click
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