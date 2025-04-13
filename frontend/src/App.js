import React, { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import NavBar from './components/NavBar';
import Rx from './components/Rx';
import NonProfit from './components/NonProfit.jsx'
import AddressSearch from './components/AddressSearch.jsx';
import Home from './components/Home.jsx';
import About from './components/About.jsx';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login.jsx'; // import your page


function App() {
  const [userDetails, setUserDetails] = useState({ name: '', role: '', address: '', email: '' }); // State for user-provided data

  const handleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        if (!userDetails.name || !userDetails.role || !userDetails.address || !userDetails.email) {
          console.error("User details are incomplete:", userDetails);
          throw new Error("User details (name, role, address, email) must be provided.");
        }

        const userInfo = await axios.get('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });

        const data = {
          unique_id: userInfo.data.sub, // From Google API
          email: userDetails.email,     // From frontend input
          name: userDetails.name,       // From frontend input
          role: userDetails.role,       // From frontend input
          address: userDetails.address, // From frontend input
        };

        fetch("http://127.0.0.1:5000/google_login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        .then(async (res) => {
          if (!res.ok) {
            const errorText = await res.text();
            console.error("Server error response:", errorText);
            throw new Error(`Server responded with status ${res.status}`);
          }
          return res.json();
        })
        .then(res => console.log("Login success:", res))
        .catch(err => console.error("Login failed:", err));
      } catch (error) {
        console.error("Error during login:", error);
      }
    },
    onError: (error) => console.error("Google login failed:", error),
  });

  const handleSignup = async (formData) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/google_login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        throw new Error('Failed to create account');
      }
      const data = await response.json();
      return data; // Return the response to handle navigation in Login.jsx
    } catch (error) {
      console.error('Signup error:', error);
      return null;
    }
  };
  
  return (
    <Router>
      <div className="App">
        <NavBar />
        <Routes>
          <Route path="/" element={<Home onGetStartedClick={() => window.location.href = '/auth'} />} />
          <Route path="/auth" element={
            <Login
              onLogin={handleLogin}
              onSignup={handleLogin}
              setUserDetails={setUserDetails} // Pass setUserDetails to Login component

            />
          } />
          <Route path="/nonprofit" element={<NonProfit />} />
          <Route path="/rx" element={<Rx />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;