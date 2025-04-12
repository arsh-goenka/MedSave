
// export default Home;
import React from 'react';
import './Home.css';

const Home = () => {
  return (
    <div className="App">
      <header className="home-header">
        {/* Left side content */}
        <div className="header-text">    
          <h1>WASTE-not-Rx</h1>
          <p>Connecting surplus medicine to communities in need</p>
          <button className="get-started-btn">Get Started</button>
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
