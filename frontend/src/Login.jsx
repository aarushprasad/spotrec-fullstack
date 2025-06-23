import React from 'react';
import './Login.css'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const Login = () => {
    const handleLogin = async () => {
        window.location.href = `${BACKEND_URL}/auth/login`;
    };

    return (
           <div className="login-page">
             <div className="login-box">
                <h1>SpotRec</h1>
                <p>Your personalized Spotify recommendation engine, built just for you.</p>
                <p>No fluff, just tunes. Discover new tracks based on your music taste, using machine learning under the hood. Our <a href="https://sites.google.com/view/spotrec/privacy-policy"> Privacy Policy </a> </p>
                <button className="login-button" onClick={handleLogin}>
                    Login with Spotify
                </button>
              </div>
            </div> 
    );
};

export default Login;
