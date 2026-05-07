import React, { useState } from 'react';
import ChatSidebar from './components/ChatSidebar';
import SpatialMap from './components/SpatialMap';
import './index.css';
import 'leaflet/dist/leaflet.css';

function App() {
  const [mapData, setMapData] = useState(null);
  
  return (
    <div className="app-container">
      <div className="chat-sidebar glass">
        <ChatSidebar setMapData={setMapData} />
      </div>
      <div className="map-container">
        <SpatialMap mapData={mapData} />
      </div>
    </div>
  );
}

export default App;
