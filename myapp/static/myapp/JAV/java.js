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



  // Formatear tamaño de archivo
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // Manejo de archivo seleccionado
        document.getElementById('fileInput').addEventListener('change', function (e) {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = formatFileSize(file.size);
                document.getElementById('fileInfo').style.display = 'block';

                // Autocompletar nombre si está vacío
                if (!document.getElementById('documentName').value) {
                    document.getElementById('documentName').value = file.name.replace(/\.[^/.]+$/, "");
                }
            }
        });

        // Drag and drop
        const dropZone = document.getElementById('uploadDropZone');

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
                document.getElementById('fileInput').files = e.dataTransfer.files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }
        });

        // Subir documento (demo)
        document.getElementById('submitUpload').addEventListener('click', function () {
            const fileInput = document.getElementById('fileInput');
            const documentName = document.getElementById('documentName').value;
            const category = document.getElementById('documentCategory').value;

            if (!fileInput.files[0]) {
                alert('Por favor selecciona un archivo');
                return;
            }

            if (!documentName) {
                alert('Por favor ingresa un nombre para el documento');
                return;
            }

            if (!category) {
                alert('Por favor selecciona una categoría');
                return;
            }

            alert('En la versión con Django, aquí se subiría el documento al servidor.\n\nDatos del documento:\n- Nombre: ' + documentName + '\n- Categoría: ' + category + '\n- Archivo: ' + fileInput.files[0].name);

            // Cerrar modal
            bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            document.getElementById('uploadForm').reset();
            document.getElementById('fileInfo').style.display = 'none';
        });

        // Filtrar por categoría
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', function () {
                document.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                const category = this.getAttribute('data-category');
                const categoryName = this.textContent.trim();

                document.getElementById('category-title').innerHTML =
                    `<i class="fas fa-file me-2"></i>${categoryName}`;

                // Filtrar documentos
                const documentCards = document.querySelectorAll('.document-card');
                documentCards.forEach(card => {
                    if (category === 'all' || card.getAttribute('data-category') === category) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });

        // Buscar documentos
        document.getElementById('searchInput').addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const documentCards = document.querySelectorAll('.document-card');

            documentCards.forEach(card => {
                const title = card.querySelector('.document-title').textContent.toLowerCase();
                const meta = card.querySelector('.document-meta').textContent.toLowerCase();

                if (title.includes(searchTerm) || meta.includes(searchTerm)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });

        // Eliminar documento
        function eliminarDocumento(button) {
            const card = button.closest('.document-card');
            const title = card.querySelector('.document-title').textContent;

            if (confirm(`¿Estás seguro de que deseas eliminar "${title}"?`)) {
                card.remove();
                alert('Documento eliminado (en la versión Django se eliminaría del servidor)');
            }
        }



        // Resetear formulario al cerrar modal
        document.getElementById('uploadModal').addEventListener('hidden.bs.modal', function () {
            document.getElementById('uploadForm').reset();
            document.getElementById('fileInfo').style.display = 'none';
        });


       document.addEventListener('DOMContentLoaded', function() {
    // Para el submenú personalizado en móvil
document.addEventListener('DOMContentLoaded', function() {
    // Toggle para submenú en móvil
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const parent = this.parentElement;
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
                submenu.classList.toggle('active');
                
                // Rotar flecha
                if (arrow) {
                    arrow.style.transform = submenu.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            }
        });
    });
    
    // Cerrar submenús al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && !e.target.closest('.has-submenu')) {
            document.querySelectorAll('.submenu.active').forEach(menu => {
                menu.classList.remove('active');
                const arrow = menu.previousElementSibling?.querySelector('.submenu-arrow');
                if (arrow) arrow.style.transform = 'rotate(0deg)';
            });
        }
    });
});});