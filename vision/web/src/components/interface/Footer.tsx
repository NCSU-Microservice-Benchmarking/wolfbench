import './Footer.css';
import React from 'react';
import { NavLink } from 'react-router-dom';

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFacebook, faLinkedin, faInstagram } from '@fortawesome/free-brands-svg-icons';

import ncsu from '../../media/images/ncsu.png';

const Footer = () => {

  return (
    <div id="footer"> 

      <div className="footer-links-mobile">
        <li><NavLink to="/about">Collaborators</NavLink></li>
        <li><NavLink to="/">Dr. Ryozhou Yu</NavLink></li>
      </div>

      <div className="footer-text"> 
        <div id="footer-credits">
          {<img className="sponsor-logo" alt="NCSU" style={{borderRadius: '5px', margin: '0 0 10px 0'}} height="200%" src={ncsu} />}
        </div>
        <h1>
          Department of Computer Science
        </h1>
        <h2>csc.ncsu.edu</h2>
      </div>

      <div className="footer-links" style={{display: window.innerWidth < 900 ? 'none' : 'flex'}}>
        <li><NavLink to="/about">Collaborators</NavLink></li>
        <li><NavLink to="https://www.csc.ncsu.edu/people/ryu5">Dr. Ryozhou Yu</NavLink></li>
      </div>

      <div className="footer-icons">
        <a href="https://www.linkedin.com/" target="_blank" rel="noreferrer">
          <FontAwesomeIcon icon={faLinkedin} size="2x" className="fa fa-facebook"/> 
        </a>
        <a href="https://www.facebook.com/" target="_blank" rel="noreferrer">
          <FontAwesomeIcon icon={faFacebook} size="2x" className="fa fa-facebook"/> 
        </a>
        <a href="https://www.instagram.com/" target="_blank" rel="noreferrer">
          <FontAwesomeIcon icon={faInstagram} size="2x"  className="fa fa-instagram"/> 
        </a>
      </div>

    </div>
  );
}
 
export default Footer;