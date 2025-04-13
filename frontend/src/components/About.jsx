import React from 'react';
import './About.css';
import Card from './Card';

const About = () => {
  return (
    <div className="about-container gradient-bg">
      <h2>Understanding the Drug Waste Crisis</h2>
      <div className="why-cards">
        <Card
          imgSrc="millMidd.webp"
          title="Millions of Medicines Wasted"
          description="Each year, billions in safe, unused medication are discarded due to overstock and expiration."
        />
        <Card
          imgSrc="peopel.webp"
          title="People Can't Afford Relief"
          description="25% of U.S. adults skip prescriptions due to cost. This isn’t okay."
        />
        <Card
          imgSrc="redis.webp"
          title="Redistribute. Restore. Reuse."
          description="We connect surplus meds with clinics and nonprofits—securely and compliantly."
        />
      </div>
    </div>
  );
};

export default About;

