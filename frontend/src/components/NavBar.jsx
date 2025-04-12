import React from 'react';
import './NavBar.css';

const NavBar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">WASTE-not-RX</div>
      <ul className="navbar-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#pharmacy">Pharmacy</a></li>
        <li><a href="#nonprofit">NonProfit</a></li>

        
      </ul>
    </nav>
  );
};

export default NavBar;