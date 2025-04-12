import React from 'react';
import NavBar from './components/NavBar';
import './App.css';

function App() {
  return (
    <div className="App">
      <NavBar />
      <header className="home-header">
        <h1>Create websites for pharmacies and nonprofits</h1>
        <p>
          Build custom, user-friendly websites that serve the unique needs of your organization.
        </p>
        <button className="get-started-btn">Get Started</button>
      </header>
    </div>
  );
}

export default App;