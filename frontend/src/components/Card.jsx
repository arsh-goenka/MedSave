import React from 'react';
import './About.css';

const Card = ({ imgSrc, title, description }) => {
  return (
    <div className="card fade-in">
      <img src={imgSrc} alt={title} className="card-img" />
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
};

export default Card;
