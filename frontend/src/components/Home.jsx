import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = ({ profile }) => {
  const navigate = useNavigate();

  return (
    <div className="App">
      <header className="home-header">
        <div className="header-text">
          <h1>WASTE-not-Rx</h1>
          <p>Connecting surplus medicine to communities in need</p>
          {profile ? (
            <div>
              <p>Welcome, {profile.name}!</p>
              <p>Welcome, {profile.email}!</p>
              <p>Welcome, {profile.id}!</p>
            </div>
          ) : (
            <button className="get-started-btn" onClick={() => navigate('/auth')}>
              Get Started
            </button>
          )}
        </div>
        {/* Right side boxes */}
        <div className="boxes-wrapper">
          <div className="box" style={{ '--box-index': 0 }}>
            <img src="sci.png" alt="Logo" className="box-image" />
            <div className="welcome-text">AI Pharma for Good</div>
            <button className="learn-more-btn">Learn More</button>
          </div>

          <div className="box" style={{ '--box-index': 1 }}>
            <img src="pills.png" alt="Logo" className="box-image" />
            <button className="learn-more-btn">Learn More</button>
          </div>
        </div>
      </header>
    </div>
  );
};

export default Home;
