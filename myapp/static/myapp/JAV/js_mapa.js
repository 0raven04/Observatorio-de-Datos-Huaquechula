document.addEventListener('DOMContentLoaded', function () {
    // Comprueba Chart y Leaflet antes de usarlos
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no cargado. Añade <script src="https://cdn.jsdelivr.net/npm/chart.js">');
    }

    if (typeof L === 'undefined') {
        console.error('Leaflet no está cargado. Añade leaflet.js antes de java.js');
        return;
    }

    const mapEl = document.getElementById('map');
    if (!mapEl) {
        console.error('Elemento #map no encontrado en el DOM.');
        return;
    }

    var puebloHuaquechula = [18.769895, -98.544040];
    var huaquechulaBounds = L.latLngBounds([
        [18.749895, -98.564040],
        [18.789895, -98.524040]
    ]);

    var map = L.map('map', {
        center: puebloHuaquechula,
        zoom: 16,
        minZoom: 14,
        maxZoom: 18,
        maxBounds: huaquechulaBounds,
        maxBoundsViscosity: 1.0
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    var customIcon = L.divIcon({
        html: '<div style="background-color: #4A4A4A; width: 24px; height: 24px; border-radius: 50%; border: 3px solid #EDEBE3;"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
    });

    L.marker(puebloHuaquechula, { icon: customIcon }).addTo(map)
        .bindPopup('<div style="text-align:center;"><h3 style="margin:0;color:#4A4A4A;">Pueblo Huaquechula</h3><p style="margin:0;">Cabecera municipal en Puebla, México</p></div>')
        .openPopup();

    L.rectangle(huaquechulaBounds, {
        color: '#e71313ff',
        fillColor: 'transparent',
        weight: 2,
        dashArray: '5,5',
        opacity: 0.7
    }).addTo(map);

    map.fitBounds(huaquechulaBounds);
    setTimeout(() => map.invalidateSize(), 300);
});

// Función para obtener parámetros de la URL (ej: ?archivo_id=5)
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

function cargarGeometrias() {
    const archivoId = getQueryParam('archivo_id');
    let urlApi = '/api/geometrias/'; // URL por defecto (todos)

    // Si hay un ID en la URL, usamos la API específica
    if (archivoId) {
        urlApi = `/api/geometrias/${archivoId}/`;
        console.log("Cargando solo archivo ID:", archivoId);
    }

    fetch(urlApi)
        .then(response => response.json())
        .then(data => {
            // ... (Aquí sigue tu código normal de Leaflet L.geoJSON) ...
            
            var capa = L.geoJSON(data, {
                // ... tus estilos y popups ...
            }).addTo(map);

            // BONUS: Hacer zoom automático a los datos cargados
            if (data.features.length > 0) {
                map.fitBounds(capa.getBounds());
            }
        })
        .catch(error => console.error('Error:', error));
}

// Ejecutar al inicio
cargarGeometrias();