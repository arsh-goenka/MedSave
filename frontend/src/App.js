import React from 'react';
import NavBar from './components/NavBar';
import Rx from './components/Rx';
import Home from './components/Home.jsx'; // Ensure this import matches the file path
import './App.css';
import NonProfit from './components/NonProfit';
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
        <Route path="/nonprofit" element={<NonProfit />} />
        <Route path="/rx" element={<Rx />} />
      </Routes>
    </div>
    </Router>
  );
}

export default App;