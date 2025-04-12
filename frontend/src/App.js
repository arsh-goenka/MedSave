import React from 'react';
import NavBar from './components/NavBar.jsx';
import Home from './components/Home.jsx'; // Ensure this import matches the file path
import './App.css';

function App() {
  return (
    <div className="App">
      <NavBar />
      <Home /> {/* Ensure this matches the exported component */}
    </div>
  );
}

export default App;