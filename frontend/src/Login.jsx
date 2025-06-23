import React from 'react';
import './Login.css'

const Login = () => {
    const handleLogin = async () => {
        window.location.href = 'http://127.0.0.1:8000/auth/login';
    };

    return (
           <div className="login-page">
             <div className="login-box">
                <h1>SpotRec</h1>
                <p>Your personalized Spotify recommendation engine, built just for you.</p>
                <p>No fluff, just tunes. Discover new tracks based on your music taste, using machine learning under the hood.</p>
                <button className="login-button" onClick={handleLogin}>
                    Login with Spotify
                </button>
              </div>
            </div> 
    );
};

export default Login;
