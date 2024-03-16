import React from 'react';
import { useNavigate } from 'react-router-dom';

const PageNotFound = () => {

  const navigate = useNavigate();

  return (  
    <div id="page-content">
      <div className="not-found">
        <h1>This page doesn't exist?</h1>
        <h2>404 Error: The requested /url destination cannot be found.</h2>
        <button
          onClick={() => navigate('/')}>
          Go Home
        </button>
      </div>
    </div>
  );
}
 
export default PageNotFound;