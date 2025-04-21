document.addEventListener("DOMContentLoaded", function () {
    const defaultLatLng = [28.6139, 77.2090]; // New Delhi

    const map = L.map('map').setView(defaultLatLng, 13);

    // Load tiles from OpenStreetMap (no key needed)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Add draggable marker
    const marker = L.marker(defaultLatLng, { draggable: true }).addTo(map);

    // Update hidden fields on drag
    function updateLatLngFields(latlng) {
        document.getElementById('latitude').value = latlng.lat;
        document.getElementById('longitude').value = latlng.lng;
    }

    updateLatLngFields(marker.getLatLng());

    marker.on('dragend', function (e) {
        updateLatLngFields(e.target.getLatLng());
    });

    // Update marker on map click
    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        updateLatLngFields(e.latlng);
    });
});
