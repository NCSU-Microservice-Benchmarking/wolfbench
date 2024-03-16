import './Header.css';

import { useEffect, useRef } from 'react';

import logo from '../../media/images/logo.png'
import { NavLink, useNavigate } from 'react-router-dom';

const Header = () => {
  
  const navigate = useNavigate();
  let lastScrollTop = useRef<number>(0);

  useEffect(() => {
    let handler = function () {
      let header = document.getElementById("header");
      if (header !== null) {
        let scrollTop = window.scrollY;
        if (lastScrollTop.current < scrollTop) {
          header.classList.remove('show-header');
          header.classList.add('hide-header');
        } else {
          header.classList.remove('hide-header');
          header.classList.add('show-header');
        }
        lastScrollTop.current = scrollTop;

      } else {
        return;
      }
    }
    document.addEventListener("scroll", handler, true);

    return () => {
      document.removeEventListener("scroll", handler);
    }
  }, []);

  return ( 
    <div id="header">
    
      <div className="banner-container" onClick={() => navigate('/')}>
        <img src={logo} height={"70%"} alt="Analyzer Logo"/>
        <div className="banner-text">
          <h1>
            Image Analyzer
          </h1>
        </div>
      </div>

      <Navbar/>

    </div>
  );
}

export default Header;


const Navbar = ()  => {
  return (
    <nav className="navbar">
      <div className="menuoptions">
        <NavLink className="navlink" to="/">Home</NavLink>
        <NavLink className="navlink" to="/docs">Docs</NavLink>
        <NavLink className="navlink" to="/about">About</NavLink>
      </div>
    </nav>
  )
}