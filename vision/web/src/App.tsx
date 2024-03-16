import AOS from 'aos'; 
import 'aos/dist/aos.css';
import './fonts.css'
import './media/loaders/macOS.css'
import './media/loaders/basic.css'

//React Hooks
import React, { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';

//UI
import Header from './components/interface/Header';
import HeaderMobile from './components/interface/Header.mobile';
import Footer from './components/interface/Footer';

//Pages
import Home from './components/pages/Main/Main';
import Docs from './components/pages/Docs/Docs';
import About from './components/pages/About/About';
import PageNotFound from './components/pages/PageNotFound';

function App() {
  
  const [dimensions, setDimensions] = useState({width: 0, height: 0});
  const breakpoint = 1100;

  const [originalFiles, setOriginalFiles] = useState<File[]>([]);
  const [resultsFiles, setResultsFiles] = useState<ArrayBuffer[]>([]);

  useEffect(() => {
    AOS.init({
      duration : 2000,
      once: true
    });
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
  }, []);

  const updateDimensions = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    setDimensions({width: width, height: height});
  }

  return ( 
    <div className="App">

      {dimensions.width > breakpoint ? 
        <Header/>
      : 
        <HeaderMobile/>
      }

      <Routes>
        <Route path="/" element={
          <Home 
            originalFiles={originalFiles} setOriginalFiles={setOriginalFiles}
            resultsFiles={resultsFiles} setResultsFiles={setResultsFiles}
          />} 
        />
        <Route path="/docs" element={<Docs/>} />
        <Route path="/about" element={<About/>} />
        <Route path="*" element={<PageNotFound/>} />
      </Routes> 

      <Footer />

    </div>
  );
}

export default App;