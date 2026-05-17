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

document.addEventListener('DOMContentLoaded', function () {
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
    // Si no hay elemento #map en esta página, salir silenciosamente.
    // Leaflet solo se carga en la vista del mapa, no en todas las páginas.
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    if (typeof L === 'undefined') {
        console.warn('Leaflet no está cargado. Incluye leaflet.js antes de java.js en la página del mapa.');
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




document.addEventListener('DOMContentLoaded', function () {
    // Formatear tamaño de archivo
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Manejo de archivo seleccionado
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const fileNameEl = document.getElementById('fileName');
                const fileSizeEl = document.getElementById('fileSize');
                const fileInfoEl = document.getElementById('fileInfo');

                if (fileNameEl) fileNameEl.textContent = file.name;
                if (fileSizeEl) fileSizeEl.textContent = formatFileSize(file.size);
                if (fileInfoEl) fileInfoEl.style.display = 'block';

                // Autocompletar nombre si está vacío
                const docNameInput = document.getElementById('documentName');
                if (docNameInput && !docNameInput.value) {
                    docNameInput.value = file.name.replace(/\.[^/.]+$/, "");
                }
            }
        });
    }

    // Drag and drop
    const dropZone = document.getElementById('uploadDropZone');
    if (dropZone) {
        dropZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.style.borderColor = 'var(--color-arena-oscuro)';
            this.style.backgroundColor = 'rgba(214, 206, 170, 0.1)';
        });

        dropZone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            this.style.borderColor = 'var(--color-beige)';
            this.style.backgroundColor = '';
        });

        dropZone.addEventListener('drop', function (e) {
            e.preventDefault();
            this.style.borderColor = 'var(--color-beige)';
            this.style.backgroundColor = '';

            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                const fInput = document.getElementById('fileInput');
                if (fInput) {
                    fInput.files = e.dataTransfer.files;
                    fInput.dispatchEvent(new Event('change'));
                }
            }
        });
    }

    // Buscar documentos
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const documentCards = document.querySelectorAll('.document-card');

            documentCards.forEach(card => {
                const titleEl = card.querySelector('.document-title');
                const metaEl = card.querySelector('.document-meta');

                if (titleEl && metaEl) {
                    const title = titleEl.textContent.toLowerCase();
                    const meta = metaEl.textContent.toLowerCase();

                    if (title.includes(searchTerm) || meta.includes(searchTerm)) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    }

    // Resetear formulario al cerrar modal
    const uploadModal = document.getElementById('uploadModal');
    if (uploadModal) {
        uploadModal.addEventListener('hidden.bs.modal', function () {
            const form = document.getElementById('uploadForm');
            const fileInfo = document.getElementById('fileInfo');
            if (form) form.reset();
            if (fileInfo) fileInfo.style.display = 'none';
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Toggle para submenú en móvil
    const submenuToggles = document.querySelectorAll('.submenu-toggle');

    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const submenu = this.nextElementSibling;
                const arrow = this.querySelector('.submenu-arrow');

                // Cerrar otros submenús abiertos
                document.querySelectorAll('.submenu.active').forEach(menu => {
                    if (menu !== submenu) {
                        menu.classList.remove('active');
                        const otherArrow = menu.previousElementSibling?.querySelector('.submenu-arrow');
                        if (otherArrow) otherArrow.style.transform = 'rotate(0deg)';
                    }
                });

                // Alternar el submenú actual
                if (submenu) submenu.classList.toggle('active');

                // Rotar flecha
                if (arrow) {
                    arrow.style.transform = submenu && submenu.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            }
        });
    });

    // Cerrar submenús al hacer clic fuera
    document.addEventListener('click', function (e) {
        if (window.innerWidth <= 768 && !e.target.closest('.has-submenu')) {
            document.querySelectorAll('.submenu.active').forEach(menu => {
                menu.classList.remove('active');
                const arrow = menu.previousElementSibling?.querySelector('.submenu-arrow');
                if (arrow) arrow.style.transform = 'rotate(0deg)';
            });
        }
    });
});


