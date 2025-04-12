import React from 'react';
import './NavBar.css';

const NavBar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">WASTE-not-RX</div>
      <ul className="navbar-links">
        <li><a href="/">Home</a></li>
        <li><a href="nonprofit">NonProfit</a></li>
        <li><a href="rx">Rx</a></li>
      </ul>
    </nav>
  );
};

export default NavBar;