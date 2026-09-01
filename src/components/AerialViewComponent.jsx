import React, { useState, useEffect } from 'react';
import { MAPS_API } from "../env";

function AerialViewComponent({ lat, lon }) {
  const [aerialViewLoaded, setAerialViewLoaded] = useState(false);
  const [error, setError] = useState(null);

  const apiKey = MAPS_API;

  useEffect(() => {
    if (lat && lon) {
      fetch(`https://maps.googleapis.com/maps/api/aerialview/v1/photo?key=${apiKey}&location=${lat},${lon}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch aerial view');
          }
          return response.json();
        })
        .then((data) => {
          // Load the aerial view image using data.link
          const image = document.createElement('img');
          image.src = data.link;
          image.alt = 'Aerial View';
          image.classList.add('w-full', 'h-64', 'object-cover', 'rounded-lg'); // Tailwind classes
          document.getElementById('aerial-view-container').appendChild(image);
          setAerialViewLoaded(true);
        })
        .catch((error) => {
          setError(error.message);
        });
    }
  }, [lat, lon]);

  return (
    <div className="relative flex flex-col w-full h-screen">
      {error && (
        <div className="absolute top-0 left-0 w-full h-full bg-red-500 text-white text-center p-4">
          {error}
        </div>
      )}
      {!aerialViewLoaded && !error && (
        <div className="absolute top-0 left-0 w-full h-full bg-gray-300 opacity-75 z-10 flex items-center justify-center">
          <p className="text-gray-600 text-lg font-semibold">Loading Aerial View...</p>
        </div>
      )}
      <div id="aerial-view-container" className="flex-grow p-4 bg-gray-100" />
    </div>
  );
}

export default AerialViewComponent;
