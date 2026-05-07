import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// إعداد الأيقونة المذهبة المحدثة
const goldIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png', 
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const COLORS = {
  PRIMARY_GREEN: '#003B38',    // أخضر الهيئة الداكن
  ACCENT_ORANGE: '#E67E51',    // البرتقالي المحروق
  MAP_STROKE: '#FFFFFF',       
  LIGHT_BG: '#F4F1EA'
};

/**
 * مكون لضبط حدود الخريطة تلقائياً لتشمل كافة البيانات
 */
const FitBoundsToData = ({ mapData }) => {
  const map = useMap();
  
  useEffect(() => {
    if (!mapData) return;
    try {
      let bounds = L.latLngBounds([]);
      
      if (mapData.geojson && mapData.geojson.features && mapData.geojson.features.length > 0) {
        const geoJsonLayer = L.geoJSON(mapData.geojson);
        bounds.extend(geoJsonLayer.getBounds());
      } 

      if (mapData.points && mapData.points.length > 0) {
        mapData.points.forEach(pt => {
            if (pt.lat && pt.lng) bounds.extend([pt.lat, pt.lng]);
        });
      }

      if (bounds.isValid()) {
        map.flyToBounds(bounds, { 
          padding: [50, 50], 
          duration: 1.5,
          easeLinearity: 0.25 
        });
      }
    } catch (e) { console.error("Error fitting bounds:", e); }
  }, [mapData, map]);
  
  return null;
};

const SpatialMap = ({ mapData }) => {
  const [allGovernorates, setAllGovernorates] = useState(null);

  useEffect(() => {
    const fetchBaseData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/governorates/all-stats');
        const data = await response.json();
        setAllGovernorates(data);
      } catch (error) { console.error("فشل جلب بيانات المحافظات:", error); }
    };
    fetchBaseData();
  }, []);

  const getBaseStyle = () => ({
    color: COLORS.PRIMARY_GREEN,
    weight: 1,
    fillColor: COLORS.PRIMARY_GREEN,
    fillOpacity: 0.05,
    interactive: false 
  });

  return (
    <MapContainer 
      center={[21.4225, 39.8261]} 
      zoom={8} 
      style={{ height: '100%', width: '100%', background: COLORS.LIGHT_BG }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; CARTO'
      />
      
      {/* 1. الطبقة الأساسية: حدود المحافظات الثابتة */}
      {allGovernorates && (
        <GeoJSON 
          data={allGovernorates} 
          style={getBaseStyle} 
        />
      )}
      
      {/* 2. الطبقة الديناميكية: GeoJSON (المراكز والمساحات) */}
      {mapData && mapData.geojson && (
        <GeoJSON 
          key={`geojson-${mapData.timestamp || 'static'}`} 
          data={mapData.geojson} 
          style={(feature) => ({
            fillColor: feature.properties.color || COLORS.ACCENT_ORANGE,
            fillOpacity: feature.properties.fillOpacity || 0.4,
            color: feature.properties.color || COLORS.ACCENT_ORANGE,
            weight: feature.properties.weight || 2,
            dashArray: feature.geometry.type === 'MultiPolygon' ? '5, 5' : '0'
          })}
          onEachFeature={(feature, layer) => {
            const name = feature.properties.NAME_AR || feature.properties.name || 'معلم مكاني';
            const govName = feature.properties.GOVERNORATE_NAME_AR || '';

            layer.bindPopup(`
              <div style="text-align: right; direction: rtl; font-family: 'Tajawal', sans-serif;">
                <b style="color:${COLORS.PRIMARY_GREEN}; font-size: 1.1rem;">مركز: ${name}</b>
                <hr style="margin: 5px 0; border: 0; border-top: 1px solid #eee;" />
                ${govName ? `<div style="margin-bottom: 5px;">🏙️ <b>المحافظة:</b> ${govName}</div>` : ''}
                <small style="color: #666;">النوع: ${feature.geometry.type === 'Point' ? 'موقع نقطي' : 'نطاق جغرافي'}</small>
                ${feature.properties.calculated_area_km2 ? `<br/><small>المساحة: ${parseFloat(feature.properties.calculated_area_km2).toFixed(2)} كم²</small>` : ''}
              </div>
            `);
          }}
        />
      )}

      {/* 3. طبقة النقاط (Markers): المدارس والخدمات */}
      {mapData && mapData.points && mapData.points.map((pt, idx) => (
        <Marker 
          key={`pt-${idx}-${pt.lat}-${mapData.timestamp}`} 
          position={[pt.lat, pt.lng]} 
          icon={goldIcon}
        >
          <Popup>
            <div style={{ textAlign: 'right', direction: 'rtl', fontFamily: 'Tajawal, sans-serif' }}>
              <strong style={{ color: COLORS.ACCENT_ORANGE, fontSize: '1rem' }}>{pt.name}</strong>
              <hr style={{ margin: '5px 0', border: '0', borderTop: '1px solid #eee' }} />
              
              <div style={{ fontSize: '0.9rem', marginBottom: '8px' }}>
                {pt.governorate && (
                  <div style={{ marginBottom: '2px' }}> <b>المحافظة:</b> {pt.governorate}</div>
                )}
                {pt.center && (
                  <div> <b>المركز:</b> {pt.center}</div>
                )}
              </div>

              <div style={{ fontSize: '0.75rem', color: '#888', background: '#f9f9f9', padding: '4px', borderRadius: '4px' }}>
                <span>إحداثيات: {pt.lat.toFixed(4)}, {pt.lng.toFixed(4)}</span>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      <FitBoundsToData mapData={mapData} />
    </MapContainer>
  );
};

export default SpatialMap;