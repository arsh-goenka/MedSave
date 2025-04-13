import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';
import About from './About';

const Home = ({ profile }) => {
  const navigate = useNavigate();

  return (
    <div className="App">
      <div className="home-background">
        <header className="home-header">
          <div className="header-text">
            <h1>MedSave</h1>
            {/* <p>Connecting surplus medicine to communities in need</p> */}

            <div className="stats-overview">
              <p><strong>MedSave Fighting Drug Waste, Fueling Health Equity</strong></p>
              {/* <p><strong>5,000+</strong> Medications Saved</p>
              <p><strong>800+</strong> Patients Helped</p> */}
            </div>

            {profile ? (
              <div>
                <p>Welcome, {profile.name}!</p>
                <p>{profile.email}</p>
                <p>ID: {profile.id}</p>
              </div>
            ) : (
              <button className="get-started-btn" onClick={() => navigate('/auth')}>Login Here!</button>
            )}

          </div>

          <div className="boxes-wrapper">
            <div className="box">
              <img src="medsafewhite.webp" alt="Scientist" className="box-image" />
              <div className="welcome-text">Pharma for Good</div>
              <button className="learn-more-btn" onClick={() => navigate('/about')}>Learn More</button>
            </div>
          </div>
        </header>

        {/* Inline About section below home header */}
        <About />
      </div>
    </div>
  );
};

export default Home;
