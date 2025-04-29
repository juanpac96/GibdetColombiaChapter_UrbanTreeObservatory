// Wait for the Leaflet map to be initialized
document.addEventListener('DOMContentLoaded', function() {
  // This will run when the page is fully loaded
  // We need to wait for the Leaflet maps to be initialized
  const checkLeaflet = setInterval(function() {
      if (window.L) {
          clearInterval(checkLeaflet);
          enhanceLeafletMaps();
      }
  }, 100);
});

function enhanceLeafletMaps() {
  // Find all Leaflet map containers
  const mapElements = document.querySelectorAll('.leaflet-container');

  mapElements.forEach(function(mapElement) {
      // Get the map instance associated with this container
      // This is a bit tricky and depends on how Django-leaflet initializes maps
      // We'll try to find it in the _leaflet_id attribute
      const mapId = mapElement._leaflet_id;
      if (!mapId || !window.L.Map._instances) return;

      const map = window.L.Map._instances[mapId];
      if (!map) return;

      // For MultiPolygon geometries, make sure we zoom to show the entire geometry
      map.on('layeradd', function(e) {
          if (e.layer && e.layer.getBounds) {
              try {
                  // Try to fit the map to the bounds of the layer
                  map.fitBounds(e.layer.getBounds(), {
                      padding: [50, 50],
                      maxZoom: 16  // Don't zoom in too much
                  });
              } catch (error) {
                  console.warn('Could not fit to bounds:', error);
              }
          }
      });

      // Add a scale control if not already present
      if (!map.scale) {
          L.control.scale().addTo(map);
      }

      // Ensure we're using OpenStreetMap tiles
      const hasOSMLayer = Object.values(map._layers).some(layer =>
          layer._url && layer._url.includes('openstreetmap.org')
      );

      if (!hasOSMLayer) {
          // Add OpenStreetMap layer if not present
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              maxZoom: 19
          }).addTo(map);

          // Remove other base layers that aren't OSM
          Object.entries(map._layers).forEach(([id, layer]) => {
              if (layer._url && !layer._url.includes('openstreetmap.org')) {
                  map.removeLayer(layer);
              }
          });
      }
  });
}
