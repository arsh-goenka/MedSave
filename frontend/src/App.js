import React from 'react';
import NavBar from './components/NavBar';
import Rx from './components/Rx';
import NavBar from './components/NavBar.jsx';
import Home from './components/Home.jsx'; // Ensure this import matches the file path
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
    <div className="App">
      <NavBar />
      <Routes>
        <Route path="/" element={
      <header className="home-header">
        <h1>Create websites for pharmacies and nonprofits</h1>
        <p>
          Build custom, user-friendly websites that serve the unique needs of your organization.
        </p>
        <button className="get-started-btn">Get Started</button>
      </header>}/>
        <Route path="/nonprofit" element={<div>NonProfit Page</div>} />
        <Route path="/rx" element={<Rx />} />
      </Routes>
      <Home /> {/* Ensure this matches the exported component */}
    </div>
    </Router>
  );
}

export default App;