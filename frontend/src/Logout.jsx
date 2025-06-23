import React from "react";
import './Logout.css'

export default function Logout() {
    const handleLogout = () => {
        const spotifyLogoutWindow = window.open(
            "https://accounts.spotify.com/en/logout",
            "Spotify Logout",
            "width=500,height=600"
        );

        setTimeout(() => {
            if (spotifyLogoutWindow) {
                spotifyLogoutWindow.close();
            }
            window.location.href = "http://127.0.0.1:8000/auth/logout";
        }, 1500);
    };

    return (
        <button className="logout-button" onClick={handleLogout}>
            Logout
        </button>
    );
}
