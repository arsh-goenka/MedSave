import React from 'react';
import './NavBar.css';

const NavBar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">Waste-not-Rx</div>
      <ul className="navbar-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#nonprofit">NonProfit</a></li>
      </ul>
    </nav>
  );
};

export default NavBar;