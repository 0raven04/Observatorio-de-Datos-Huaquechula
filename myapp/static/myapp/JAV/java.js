document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');
    
    function updateNavbar() {
        const isDesktop = window.innerWidth >= 768;
        const shouldScroll = window.scrollY > 100 && isDesktop;
        
        // Usar solo una clase para mejor control
        if (shouldScroll) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    // Event listeners
    window.addEventListener('scroll', updateNavbar);
    window.addEventListener('resize', updateNavbar);
    
    // Aplicar al cargar
    updateNavbar();
});

document.addEventListener('DOMContentLoaded', function() {
            // Gráfica de barras - Visitantes por mes
            const ctx1 = document.getElementById('chart1');
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                    datasets: [{
                        label: 'Visitantes',
                        data: [1200, 1500, 1800, 2100, 2500, 3000, 3500, 3200, 2800, 2200, 1800, 1500],
                        backgroundColor: '#D35400',
                        borderColor: '#D35400',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Gráfica de línea - Tendencia anual
            const ctx2 = document.getElementById('chart2');
            if (ctx2) {
                new Chart(ctx2, {
                    type: 'line',
                    data: {
                        labels: ['2020', '2021', '2022', '2023', '2024'],
                        datasets: [{
                            label: 'Crecimiento anual',
                            data: [15000, 18000, 21000, 24000, 28000],
                            borderColor: '#4A4A4A',
                            backgroundColor: 'rgba(74, 74, 74, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: false
                            }
                        }
                    }
                });
            }
        });

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
        color: '#4A4A4A',
        fillColor: 'transparent',
        weight: 2,
        dashArray: '5,5',
        opacity: 0.7
    }).addTo(map);

    map.fitBounds(huaquechulaBounds);
    setTimeout(() => map.invalidateSize(), 300);
});
