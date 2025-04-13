import React, { useState } from "react";
import { Send, AlertCircle } from 'lucide-react';
import AddressSearch from './AddressSearch.jsx';
import './Rx.css'

const Rx = () => {
    // names of consts have to be same as Flask backend
    const [formData, setFormData] = useState({
      pharmacy_name: '',
      address: '',
      product_ndc: '',
      quantity: '',
      price: '',
      pharmacy_expiration: ''
    });
    
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState(null);
  
    const handleChange = (e) => {
      const { name, value } = e.target;
      setFormData(prevData => ({
        ...prevData,
        [name]: value
      }));
    };

    const handleAddressSelect = (address) => {
        setFormData(prevData => ({
          ...prevData,
          address: address
        }));
      };
      
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      setError(null);
      setSuccess(false);
      
      try {
        // Assuming your Flask backend is running at this URL
        // You would replace this with your actual endpoint
        const response = await fetch('http://127.0.0.1:5000/medicines', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
        
        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Success:', result);
        setSuccess(true);
        
        // Reset form after successful submission
        setFormData({
          pharmacy_name: '',
          address: '',
          product_ndc: '',
          quantity: '',
          price: '',
          pharmacy_expiration: ''
        });
        
      } catch (error) {
        console.error('Error:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
  
    return (
        <div className="py-3  nonprofit-container">
      <div className="w-full max-w-lg max-h-lg mx-auto bg-white rounded-lg shadow-md p-4">
        <h2 className="text-2xl font-bold text-blue-800 mb-6">Prescription Information</h2>
      
        {success && (
          <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4">
            Prescription data successfully submitted!
          </div>
        )}
        
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 flex items-center">
            <AlertCircle className="mr-2" size={20} />
            <span>Error: {error}</span>
          </div>
        )}
        
        {/** This is the code for the submit form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div> {/** This is the div for name of pharmacy*/}
            <div className="flex justify-center items-center">
            <input 
              type="text"
              id="pharmacy_name"
              name="pharmacy_name"
              placeholder="Pharmacy Name"
              value={formData.pharmacy_name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            /></div>
          </div>
          
          {/**<div> {/** This is the div for the address of the pharmacy 
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
              Pharmacy Address
            </label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              rows="2"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>*/}
          <div>
            <AddressSearch onAddressSelect={handleAddressSelect}/>
          </div>

          <div> {/** This is the div for the NDC */}
            <div className="flex justify-center items-center">
            <input
              type="text"
              id="product_ndc"
              placeholder="Product NDC"
              name="product_ndc"
              value={formData.product_ndc}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            /></div>
          </div>
          
          <div className="grid grid-cols-2 gap-4"> {/** div for both Quantity and Price */}
            <div> {/**  */}
              <div className="flex justify-center items-center">
              <input
                type="number"
                id="quantity"
                name="quantity"
                placeholder="Quantity"
                value={formData.quantity}
                onChange={handleChange}
                min="1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                required
              /></div>
            </div>
            
            <div>
              <div className="flex justify-center items-center">
              <input
                type="number"
                id="price"
                name="price"
                placeholder="Price ($)"
                value={formData.price}
                onChange={handleChange}
                min="0.01"
                step="0.01"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                required
              /></div>
            </div>
          </div>
          
          <div> {/** div for expiration date */}
            <div className="flex justify-center items-center">
            <input
              type="date"
              id="pharmacy_expiration"
              name="pharmacy_expiration"
              placeholder="Expiration Date"
              value={formData.pharmacy_expiration}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg placeholder-gray-400 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            /></div>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className={`w-full flex justify-center items-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </>
            ) : (
              <>
                <Send size={18} className="mr-2" />
                Submit Prescription
              </>
            )}
          </button>
        </form>
      </div>
      </div>
    );
  };

export default Rx;