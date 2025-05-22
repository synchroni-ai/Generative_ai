import React from 'react';
import './footer.css';
import footer_logo from '../asessts/images/logo1.png';
 
const Footer = () => {
  return (
    <div className='Footer_paragraph'>
      <img src={footer_logo} alt="Footer Logo" className='footer-logo' />
      <p className='footer-text'>© 2025 Inc. All rights reserved.</p>
    </div>
  );
};
 
export default Footer;
 