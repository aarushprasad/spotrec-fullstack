import React from "react";
import './Logout.css'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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
            window.location.href = `${BACKEND_URL}/auth/logout`;
        }, 1500);
    };

    return (
        <button className="logout-button" onClick={handleLogout}>
            Logout
        </button>
    );
}
