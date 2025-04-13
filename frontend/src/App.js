import React from 'react';
import NavBar from './components/NavBar';
import Rx from './components/Rx';
import AddressSearch from './components/AddressSearch.jsx';
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
          <Home /> 
        }/>
        <Route path="/nonprofit" element={<div>NonProfit Page</div>} />
        <Route path="/rx" element={<Rx />} />
        <Route path="/address" element={<AddressSearch />} />
      </Routes>
    </div>
    </Router>
  );
}

export default App;