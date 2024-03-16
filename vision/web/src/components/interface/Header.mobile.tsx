import './Header.mobile.css';

import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { NavLink } from 'react-router-dom';

import logo from '../../media/images/logo.png';

const HeaderMobile = () => {

  const navigate = useNavigate();

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  let navmenu = document.getElementById("nav-menu-mobile");
  let navbtn = document.querySelector(".nav-dropbtn-mobile");

  const openMenu = () => {
    let body = document.getElementById("page-content");
    navbtn!.classList.remove('menu-closed');
    navbtn!.classList.add('menu-open');
    navmenu!.classList.remove("slide-out-menu");
    navmenu!.classList.add("slide-in-menu");
    navmenu!.classList.remove('hide-element');
    navmenu!.classList.add('show-blockelement');
    body!.style.pointerEvents = "none";
    document.body.style.overflow = "hidden";
    setIsMenuOpen(true);
  }

  const closeMenu = () => {
    var body = document.getElementById("page-content");
    navbtn!.classList.remove('menu-open');
    navbtn!.classList.add('menu-closed');
    navmenu!.classList.remove("slide-in-menu");
    navmenu!.classList.add("slide-out-menu");
    setTimeout(function(){
      navmenu!.classList.remove('show-blockelement');
      navmenu!.classList.add("hide-element");
    }, 200); 
    body!.style.pointerEvents = "auto";
    document.body.style.overflow = "auto";
    setIsMenuOpen(false);
  }

  const showNavigation = () => {
    if (!isMenuOpen){
      openMenu();
    } else {
      closeMenu();
    }
  }


  return (
    <>
      <div className="header-bar-mobile">

        <div className="logo-mobile" 
          onClick={() => {navigate('/'); closeMenu()}}
        >
          <img src={logo} height={"70%"} alt="Analyzer Logo"/>
          <div className="banner-text">
          </div>
        </div>

        <button className="nav-dropbtn-mobile menu-closed"
          onClick={showNavigation}
        ></button>

      </div>

      <div id="nav-menu-mobile" className="hide-element slide-in-menu">
        <div id="small-seperator" style={{width: "100%", padding: "0", background: '#CC0000'}}></div>

        <div className="menu-options-mobile">
          <ul style={{listStyleType: "none", padding: "0 0 0 2vh", marginTop: '20px', textAlign: "center"}}>
            <li><NavLink className="navlink-mobile" onClick={closeMenu} to="/" >Home</NavLink></li>
            <li><NavLink className="navlink-mobile" onClick={closeMenu} to="/docs">Docs</NavLink></li>
            <li><NavLink className="navlink-mobile" onClick={closeMenu} to="/about">About</NavLink></li>
          </ul>
        </div>
      </div>
    </>
  );
}
 
export default HeaderMobile;