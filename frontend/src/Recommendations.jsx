import React, { useEffect, useState } from 'react';
import './Recommendations.css';
import { getRecommendations } from './api';

export default function Recommendations() {
  const [trackIds, setTrackIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [focusedIndex, setFocusedIndex] = useState(0);

  useEffect(() => {
    getRecommendations()
      .then((data) => {
        setTrackIds(data.recommended_track_ids || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('fetch error:', err);
        setError('Failed to load recommendations');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const iframes = Array.from(document.querySelectorAll('.spotify-embed'));
      let minDistance = Infinity;
      let indexInFocus = 0;

      iframes.forEach((iframe, index) => {
        const rect = iframe.getBoundingClientRect();
        const distance = Math.abs(rect.top + rect.height / 2 - window.innerHeight / 2);
        if (distance < minDistance) {
          minDistance = distance;
          indexInFocus = index;
        }
      });

      setFocusedIndex(indexInFocus);
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll();

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (loading) return <div className="status-msg">Loading recommendations...</div>;
  if (error) return <div className="status-msg">{error}</div>;

  return (
    <div className="recommendations-wrapper">
      <h2>Personalized Recommendations</h2>
      <h4>Extrapolated from your liked tracks. These might take a few seconds to load.</h4>
      <div className="recommendations-container">
        {trackIds.map((id, idx) => (
          <iframe
            key={id}
            className={`spotify-embed ${idx === focusedIndex ? 'focused' : ''}`}
            src={`https://open.spotify.com/embed/track/${id}`}
            width="1300"
            height="400"
            frameBorder="0"
            allowtransparency="true"
            allow="encrypted-media"
            style={{
              transform: idx === focusedIndex ? 'scale(1.05)' : 'scale(0.9)',
              transition: 'transform 0.3s ease-in-out',
              transformOrigin: 'left center',
            }}
          />
        ))}
      </div>
    </div>
  );
}

