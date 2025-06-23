import React, { useEffect, useState } from "react";
import Recommendations from "./Recommendations";
import Login from "./Login";
import Logout from "./Logout";
import './App.css';
import { getRecommendations } from "./api"; // bring this in!

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(null);

  useEffect(() => {
    getRecommendations()
      .then(() => {
        console.log("Logged in!");
        setIsLoggedIn(true);
      })
      .catch(() => {
        console.log("Not logged in!");
        setIsLoggedIn(false);
      });
  }, []);

  if (isLoggedIn === null) return <div className="checking-login-msg">Checking login...</div>;

  console.log("isLoggedIn:", isLoggedIn);
  return isLoggedIn ? (<div className="app-container"> <Logout /> <Recommendations /> </div>) : <Login />;
}

export default App;
