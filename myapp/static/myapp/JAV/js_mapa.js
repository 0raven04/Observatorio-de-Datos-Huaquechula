


if (!window._mapaYaInicializado) {
    window._mapaYaInicializado = true;

    document.addEventListener('DOMContentLoaded', function() {
        
        // 1. CONFIGURACIÓN DEL MAPA
        var centroHuaquechula = [18.769895, -98.544040];
        var limitesMapa = L.latLngBounds([
            [18.749895, -98.564040], [18.789895, -98.524040]
        ]);

        if (window._leaflet_map_instance) {
            try { window._leaflet_map_instance.remove(); } catch (e) { }
            window._leaflet_map_instance = null;
        }

        var mapContainer = document.getElementById('map');
        if (mapContainer) { mapContainer.innerHTML = ''; }

        var map = L.map('map', {
            center: centroHuaquechula, zoom: 16, minZoom: 14, maxZoom: 18,
            maxBounds: limitesMapa, maxBoundsViscosity: 1.0, zoomControl: true
        });
        window._leaflet_map_instance = map;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors', maxZoom: 19
        }).addTo(map);

        var iconoCentro = L.divIcon({
            html: '<div style="background-color: #4A4A4A; width: 24px; height: 24px; border-radius: 50%; border: 3px solid #EDEBE3;"></div>',
            className: '', iconSize: [24, 24], iconAnchor: [12, 12], popupAnchor: [0, -12]
        });
        L.marker(centroHuaquechula, { icon: iconoCentro }).addTo(map)
            .bindPopup('<div style="text-align:center;"><strong>Pueblo Huaquechula</strong><br>Cabecera municipal</div>');

        L.rectangle(limitesMapa, { color: '#e71313', weight: 2, dashArray: '5, 5', fill: false, opacity: 0.6 }).addTo(map);

        // 2. DATOS
        try {
            var rawData = '{{ geojson_data|safe }}';
            var categoriasSitio_BD = JSON.parse('{{ categorias_sitio|safe }}');
            var sitiosTuristicos_BD = JSON.parse('{{ sitios_turisticos|safe }}');
            
            var gruposPorTipo = {
                'sitio_turistico': L.layerGroup().addTo(map),
                'ofrenda': L.layerGroup().addTo(map),
                'servicio': L.layerGroup().addTo(map),
                'general': L.layerGroup().addTo(map)
            };
            
            var gruposSubCategorias = {};
            if (categoriasSitio_BD) {
                categoriasSitio_BD.forEach(function(cat) {
                    gruposSubCategorias[cat.id] = L.layerGroup().addTo(map);
                });
            }

            var todosLosPuntos = [];

            function obtenerColor(cat) {
                if (!cat) return "#3388ff";
                cat = cat.toLowerCase();
                if (cat.includes('ofrenda')) return "#ff7800";
                if (cat.includes('servicio')) return "#28a745";
                if (cat.includes('sitio')) return "#e91e63";
                return "#6c757d";
            }

            if (rawData && rawData !== '{}' && rawData !== 'null') {
                var geojsonData = JSON.parse(rawData);
                if (geojsonData.features) {
                    L.geoJSON(geojsonData, {
                        style: function(f) {
                            var cat = f.properties.categoria || 'general';
                            return { color: obtenerColor(cat), weight: 4, opacity: 0.8 };
                        },
                        onEachFeature: function(f, layer) {
                            var p = f.properties;
                            
                            var html = "<div style='text-align:center; min-width:150px;'><h4>" + (p.nombre || "Sin nombre") + "</h4>";
                            if(p.imagen) html += "<img src='" + p.imagen + "' style='width:100%; height:100px; object-fit:cover; border-radius:4px;'>";
                            if(p.horario) html += "<div style='font-size:12px; margin-top:5px;'>🕒 " + p.horario + "</div>";
                            html += "</div>";
                            layer.bindPopup(html);

                            var tipo = p.categoria || 'general';
                            if (gruposPorTipo[tipo]) gruposPorTipo[tipo].addLayer(layer);

                            if (tipo === 'sitio_turistico' && p.id_categoria_bd) {
                                if (gruposSubCategorias[p.id_categoria_bd]) gruposSubCategorias[p.id_categoria_bd].addLayer(layer);
                            }
                            todosLosPuntos.push(layer);
                        },
                        pointToLayer: function (f, latlng) {
                            var cat = f.properties.categoria || 'general';
                            return L.circleMarker(latlng, { radius: 8, fillColor: obtenerColor(cat), color: "#fff", weight: 1, opacity: 1, fillOpacity: 0.9 });
                        }
                    });
                }
            }

            // =========================================================
            // 3. CONTROL DE FILTROS (CON SCROLL CORREGIDO)
            // =========================================================
            var ControlFiltros = L.Control.extend({
                onAdd: function(map) {
                    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                    
                    container.style.backgroundColor = 'white';
                    container.style.width = '34px';
                    container.style.height = '34px';
                    container.style.overflow = 'hidden';
                    container.style.transition = 'width 0.3s, height 0.3s';
                    container.style.cursor = 'pointer';
                    container.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)';
                    
                    // ICONO
                    var iconDiv = L.DomUtil.create('div', 'filter-icon', container);
                    iconDiv.innerHTML = '<i class="fas fa-filter" style="font-size:16px; line-height:34px; width:34px; text-align:center; color:#333;"></i>';

                    // --- PANEL DE CONTENIDO (ESTADO EXPANDIDO) ---
                    var panel = L.DomUtil.create('div', 'filter-panel', container);
                    panel.style.display = 'none';
                    panel.style.padding = '10px';
                    panel.style.minWidth = '220px';
                    
                    // *** AQUÍ ESTÁ LA CORRECCIÓN DEL SCROLL ***
                    panel.style.maxHeight = '60vh';   // Máximo 60% de la altura de pantalla
                    panel.style.overflowY = 'auto';   // Scroll vertical
                    panel.style.overflowX = 'hidden'; // Sin scroll horizontal
                    // *******************************************

                    var header = document.createElement('div');
                    header.innerHTML = '<strong style="font-size:14px;">Filtrar Mapa</strong> <span style="float:right; cursor:pointer;" id="close-filter">✖</span>';
                    header.style.marginBottom = '10px';
                    header.style.borderBottom = '1px solid #eee';
                    header.style.paddingBottom = '5px';
                    panel.appendChild(header);

                    // 1. FILTROS PRINCIPALES
                    var tiposDiv = document.createElement('div');
                    tiposDiv.innerHTML = '<div style="font-size:12px; font-weight:bold; color:#666; margin-bottom:5px;">TIPOS PRINCIPALES</div>';
                    
                    function crearCheckTipo(label, key, color) {
                        var div = document.createElement('div');
                        div.innerHTML = `<label style="cursor:pointer; display:block; margin-bottom:5px; font-size:13px;">
                            <input type="checkbox" checked onchange="toggleLayer('${key}', this.checked)"> 
                            <span style="color:${color};">●</span> ${label}
                        </label>`;
                        return div;
                    }

                    var cSitios = sitiosTuristicos_BD ? sitiosTuristicos_BD.length : 0;
                    var cOfrendas = '{{ ofrendas|length }}'; 
                    var cServicios = '{{ servicios|length }}';

                    tiposDiv.appendChild(crearCheckTipo('Sitios Turísticos (' + cSitios + ')', 'sitio_turistico', '#e91e63'));
                    tiposDiv.appendChild(crearCheckTipo('Ofrendas (' + cOfrendas + ')', 'ofrenda', '#ff7800'));
                    tiposDiv.appendChild(crearCheckTipo('Servicios (' + cServicios + ')', 'servicio', '#28a745'));
                    panel.appendChild(tiposDiv);

                    // 2. SUB-CATEGORÍAS
                    if (categoriasSitio_BD && categoriasSitio_BD.length > 0) {
                        var subDiv = document.createElement('div');
                        subDiv.id = 'subcategorias-panel';
                        subDiv.style.marginTop = '15px';
                        subDiv.style.paddingLeft = '15px';
                        subDiv.style.borderLeft = '2px solid #eee';
                        subDiv.innerHTML = '<div style="font-size:12px; font-weight:bold; color:#666; margin-bottom:5px;">CATEGORÍAS DE SITIO</div>';
                        
                        categoriasSitio_BD.forEach(function(cat) {
                            var count = sitiosTuristicos_BD ? sitiosTuristicos_BD.filter(s => s.categoria_id === cat.id).length : 0;
                            var div = document.createElement('div');
                            div.innerHTML = `<label style="cursor:pointer; display:block; margin-bottom:3px; font-size:13px;">
                                <input type="checkbox" checked onchange="toggleSubLayer(${cat.id}, this.checked)"> ${cat.nombre} <span style="color:#999; font-size:11px;">(${count})</span>
                            </label>`;
                            subDiv.appendChild(div);
                        });
                        panel.appendChild(subDiv);
                    }

                    // Eventos de apertura/cierre
                    var expanded = false;
                    container.onclick = function(e) {
                        if (!expanded) {
                            expanded = true;
                            container.style.width = 'auto';
                            container.style.height = 'auto'; // Deja que crezca con el max-height
                            iconDiv.style.display = 'none';
                            panel.style.display = 'block';
                        }
                    };

                    header.querySelector('#close-filter').onclick = function(e) {
                        e.stopPropagation();
                        expanded = false;
                        panel.style.display = 'none';
                        iconDiv.style.display = 'block';
                        container.style.width = '34px';
                        container.style.height = '34px';
                    };

                    // Deshabilitar propagación de scroll al mapa (IMPORTANTE)
                    L.DomEvent.disableClickPropagation(container);
                    L.DomEvent.disableScrollPropagation(container);

                    return container;
                }
            });

            // Funciones globales
            window.toggleLayer = function(key, checked) {
                if (checked) map.addLayer(gruposPorTipo[key]);
                else map.removeLayer(gruposPorTipo[key]);
                
                if (key === 'sitio_turistico') {
                    var panelSub = document.getElementById('subcategorias-panel');
                    if(panelSub) panelSub.style.display = checked ? 'block' : 'none';
                }
            };

            window.toggleSubLayer = function(id, checked) {
                if (gruposSubCategorias[id]) {
                    if (checked) map.addLayer(gruposSubCategorias[id]);
                    else map.removeLayer(gruposSubCategorias[id]);
                }
            };

            map.addControl(new ControlFiltros({ position: 'topright' }));

            if (todosLosPuntos.length > 0) {
                var grupoTemp = L.featureGroup(todosLosPuntos);
                var boundsDatos = grupoTemp.getBounds();
                if (limitesMapa.intersects(boundsDatos)) {
                    map.fitBounds(boundsDatos, { padding: [50, 50], maxZoom: 18 });
                }
            }

        } catch (e) {
            console.error("Error mapa:", e);
        }
    });
}

// =====================================================
// SISTEMA DE RESEÑAS GLOBALES
// =====================================================
(function () {
    'use strict';

    // -- Utilidades --
    var ETIQUETAS_ESTRELLAS = ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', '¡Excelente!'];
    var COLORES_AVATAR = [
        '#e91e63','#9c27b0','#3f51b5','#2196f3','#00bcd4',
        '#009688','#4caf50','#ff9800','#795548','#607d8b'
    ];

    function colorAvatar(nombre) {
        var hash = 0;
        for (var i = 0; i < (nombre || '').length; i++) {
            hash = nombre.charCodeAt(i) + ((hash << 5) - hash);
        }
        return COLORES_AVATAR[Math.abs(hash) % COLORES_AVATAR.length];
    }

    function iniciales(nombre) {
        var partes = (nombre || 'V').trim().split(/\s+/);
        if (partes.length === 1) return partes[0].charAt(0).toUpperCase();
        return (partes[0].charAt(0) + partes[partes.length - 1].charAt(0)).toUpperCase();
    }

    function estrellasFill(n) {
        return '★'.repeat(n) + '☆'.repeat(5 - n);
    }

    function getCsrf() {
        var cookies = document.cookie.split(';');
        for (var c of cookies) {
            var kv = c.trim().split('=');
            if (kv[0] === 'csrftoken') return decodeURIComponent(kv[1]);
        }
        return '';
    }

    function mostrarToast(msg, icono) {
        var t = document.getElementById('resena-toast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'resena-toast';
            document.body.appendChild(t);
        }
        t.innerHTML = '<i class="fas fa-' + (icono || 'check-circle') + '"></i> ' + msg;
        t.style.display = 'flex';
        clearTimeout(t._timeout);
        t._timeout = setTimeout(function () { t.style.display = 'none'; }, 3200);
    }

    // -- Estado --
    var calificacionSeleccionada = 0;

    // -- DOM refs (se asignan tras DOMContentLoaded) --
    var panelResenas, fabResenas, btnCerrarPanel, btnDejarResena;
    var modalOverlay, btnCerrarModal, btnEnviar;
    var inputComentario, charCountEl, starPickLabel;
    var errorEl, stars;
    var prFeed, prLoading;
    var prScoreNum, prEstrellasProm, prTotal;
    var bars = {};

    // -- Abrir / cerrar panel --
    function abrirPanel() {
        if (!panelResenas) return;
        panelResenas.classList.add('pr-visible');
        cargarResenas();
    }

    function cerrarPanel() {
        if (panelResenas) panelResenas.classList.remove('pr-visible');
    }

    // -- Abrir / cerrar modal --
    function abrirModal() {
        resetModal();
        if (modalOverlay) modalOverlay.classList.add('modal-visible');
        // Re-render reCAPTCHA si ya fue completado antes
        if (window.grecaptcha) {
            try { grecaptcha.reset(); } catch (e) {}
        }
    }

    function cerrarModal() {
        if (modalOverlay) modalOverlay.classList.remove('modal-visible');
    }

    function resetModal() {
        calificacionSeleccionada = 0;
        if (stars) stars.forEach(function (s) { s.classList.remove('selected', 'hover'); });
        if (starPickLabel) { starPickLabel.textContent = 'Selecciona una calificación'; starPickLabel.classList.remove('filled'); }
        if (inputComentario) inputComentario.value = '';
        if (charCountEl) charCountEl.textContent = '0';
        if (errorEl) errorEl.style.display = 'none';
        if (btnEnviar) { btnEnviar.disabled = false; btnEnviar.classList.remove('enviando'); btnEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar reseña'; }
    }

    // -- Estrellas interactivas --
    function initStars() {
        if (!stars) return;
        stars.forEach(function (s, idx) {
            s.addEventListener('mouseenter', function () {
                stars.forEach(function (x, i) { x.classList.toggle('hover', i <= idx); });
            });
            s.addEventListener('mouseleave', function () {
                stars.forEach(function (x, i) { x.classList.remove('hover'); x.classList.toggle('selected', i < calificacionSeleccionada); });
            });
            s.addEventListener('click', function () {
                calificacionSeleccionada = idx + 1;
                stars.forEach(function (x, i) { x.classList.toggle('selected', i < calificacionSeleccionada); });
                if (starPickLabel) {
                    starPickLabel.textContent = ETIQUETAS_ESTRELLAS[calificacionSeleccionada];
                    starPickLabel.classList.add('filled');
                }
            });
        });
    }

    // -- Cargar reseñas del servidor --
    function cargarResenas() {
        if (prLoading) prLoading.style.display = 'block';
        if (prFeed) prFeed.innerHTML = '<div class="pr-loading" id="pr-loading"><i class="fas fa-circle-notch fa-spin"></i> Cargando reseñas...</div>';
        prLoading = document.getElementById('pr-loading');

        fetch('/api/resenas/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function (r) { return r.json(); })
            .then(function (data) { renderizarStats(data); renderizarFeed(data.resenas); })
            .catch(function () {
                if (prFeed) prFeed.innerHTML = '<div class="pr-empty"><i class="fas fa-wifi"></i>No se pudieron cargar las reseñas.</div>';
            });
    }

    // -- Renderizar estadísticas y barras --
    function renderizarStats(data) {
        if (prScoreNum) prScoreNum.textContent = data.total > 0 ? data.promedio : '—';
        if (prEstrellasProm) prEstrellasProm.textContent = data.total > 0 ? estrellasFill(Math.round(data.promedio)) : '☆☆☆☆☆';
        if (prTotal) prTotal.textContent = data.total > 0 ? data.total + ' reseña' + (data.total !== 1 ? 's' : '') : 'Sin reseñas aún';

        [5,4,3,2,1].forEach(function (n) {
            var bar = bars[n];
            if (!bar) return;
            var pct = data.total > 0 ? Math.round((data.distribucion[String(n)] / data.total) * 100) : 0;
            bar.style.width = pct + '%';
        });
    }

    // -- Renderizar feed de tarjetas --
    function renderizarFeed(resenas) {
        if (!prFeed) return;
        if (!resenas || resenas.length === 0) {
            prFeed.innerHTML = '<div class="pr-empty"><i class="fas fa-star"></i>Sé el primero en opinar sobre Huaquechula</div>';
            return;
        }
        prFeed.innerHTML = '';
        resenas.forEach(function (r) { insertarTarjeta(r, false); });
    }

    // -- Insertar tarjeta al feed (top o bottom) --
    function insertarTarjeta(r, alTop) {
        if (!prFeed) return;
        var color = colorAvatar(r.autor);
        var inic = iniciales(r.autor);
        var card = document.createElement('div');
        card.className = 'resena-card';
        card.id = 'resena-card-' + r.id;
        card.innerHTML =
            '<div class="resena-avatar" style="background:' + color + ';">' + inic + '</div>' +
            '<div class="resena-content">' +
                '<div class="resena-top">' +
                    '<span class="resena-autor" title="' + escHtml(r.autor) + '">' + escHtml(r.autor) + '</span>' +
                    '<span class="resena-fecha">' + escHtml(r.fecha) + '</span>' +
                '</div>' +
                '<div class="resena-stars">' + estrellasFill(r.calificacion) + '</div>' +
                (r.comentario ? '<p class="resena-texto">' + escHtml(r.comentario) + '</p>' : '') +
                '<div class="resena-actions">' +
                    '<button class="resena-btn-like" data-id="' + r.id + '" title="Me gusta"><i class="fas fa-heart"></i> <span class="like-count">' + r.likes + '</span></button>' +
                    '<button class="resena-btn-report" data-id="' + r.id + '" title="Reportar"><i class="fas fa-flag"></i> Reportar</button>' +
                '</div>' +
            '</div>';

        card.querySelector('.resena-btn-like').addEventListener('click', function () { darLike(r.id, this); });
        card.querySelector('.resena-btn-report').addEventListener('click', function () { reportarResena(r.id); });

        if (alTop && prFeed.firstChild) {
            prFeed.insertBefore(card, prFeed.firstChild);
        } else {
            prFeed.appendChild(card);
        }
    }

    function escHtml(str) {
        return String(str || '')
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // -- Dar like --
    function darLike(id, btn) {
        fetch('/api/resenas/' + id + '/like/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrf(), 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) {
                var countEl = btn.querySelector('.like-count');
                if (countEl) countEl.textContent = data.likes;
                btn.style.color = '#e91e63';
                btn.disabled = true;
            }
        })
        .catch(function () {});
    }

    // -- Reportar reseña --
    function reportarResena(id) {
        if (!confirm('¿Deseas reportar esta reseña como inapropiada?')) return;
        fetch('/api/resenas/' + id + '/reportar/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrf(), 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) mostrarToast('Reseña reportada. Gracias por tu aviso.', 'flag');
        })
        .catch(function () {});
    }

    // -- Enviar nueva reseña --
    function enviarResena() {
        var comentario = (inputComentario ? inputComentario.value.trim() : '');

        if (!calificacionSeleccionada) { mostrarError('Selecciona una calificación.'); return; }

        var recaptchaToken = '';
        if (window.grecaptcha) {
            try { recaptchaToken = grecaptcha.getResponse(); } catch (e) {}
        }
        if (!recaptchaToken) { mostrarError('Completa el reCAPTCHA.'); return; }

        if (btnEnviar) { btnEnviar.disabled = true; btnEnviar.classList.add('enviando'); btnEnviar.innerHTML = 'Enviando...'; }
        if (errorEl) errorEl.style.display = 'none';

        fetch('/api/resenas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrf(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                nombre_visitante: '',
                calificacion: calificacionSeleccionada,
                comentario: comentario,
                recaptcha_token: recaptchaToken
            })
        })
        .then(function (r) { return r.json().then(function (d) { return { status: r.status, data: d }; }); })
        .then(function (res) {
            if (res.status === 201 && res.data.ok) {
                cerrarModal();
                insertarTarjeta(res.data.resena, true);
                // Actualizar promedio y total localmente (fetch completo)
                cargarResenas();
                mostrarToast('¡Gracias por tu reseña! 🌟', 'star');
            } else {
                mostrarError(res.data.error || 'Ocurrió un error. Intenta de nuevo.');
                if (window.grecaptcha) { try { grecaptcha.reset(); } catch (e) {} }
                if (btnEnviar) { btnEnviar.disabled = false; btnEnviar.classList.remove('enviando'); btnEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar reseña'; }
            }
        })
        .catch(function () {
            mostrarError('Sin conexión. Verifica tu internet.');
            if (btnEnviar) { btnEnviar.disabled = false; btnEnviar.classList.remove('enviando'); btnEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar reseña'; }
        });
    }

    function mostrarError(msg) {
        if (errorEl) { errorEl.textContent = msg; errorEl.style.display = 'block'; }
    }

    // -- Init al cargar el DOM --
    document.addEventListener('DOMContentLoaded', function () {
        panelResenas   = document.getElementById('panel-resenas');
        fabResenas     = document.getElementById('fab-resenas');
        btnCerrarPanel = document.getElementById('btn-cerrar-resenas');
        btnDejarResena = document.getElementById('btn-dejar-resena');
        modalOverlay   = document.getElementById('modal-resena-overlay');
        btnCerrarModal = document.getElementById('btn-cerrar-modal');
        btnEnviar      = document.getElementById('btn-enviar-resena');
        inputComentario= document.getElementById('resena-comentario');
        charCountEl    = document.getElementById('char-count');
        starPickLabel  = document.getElementById('star-pick-label');
        errorEl        = document.getElementById('resena-error');
        stars          = Array.from(document.querySelectorAll('.star-pick'));
        prFeed         = document.getElementById('pr-feed');
        prLoading      = document.getElementById('pr-loading');
        prScoreNum     = document.getElementById('pr-score-num');
        prEstrellasProm= document.getElementById('pr-estrellas-prom');
        prTotal        = document.getElementById('pr-total');
        bars = { 5: document.getElementById('bar5'), 4: document.getElementById('bar4'),
                 3: document.getElementById('bar3'), 2: document.getElementById('bar2'),
                 1: document.getElementById('bar1') };

        initStars();

        // Contador de caracteres
        if (inputComentario && charCountEl) {
            inputComentario.addEventListener('input', function () {
                charCountEl.textContent = this.value.length;
            });
        }

        // FAB → abrir panel
        if (fabResenas) fabResenas.addEventListener('click', abrirPanel);

        // Cerrar panel
        if (btnCerrarPanel) btnCerrarPanel.addEventListener('click', cerrarPanel);

        // Abrir modal de reseña
        if (btnDejarResena) btnDejarResena.addEventListener('click', abrirModal);

        // Cerrar modal con botón X
        if (btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModal);

        // Cerrar modal al clic en overlay
        if (modalOverlay) {
            modalOverlay.addEventListener('click', function (e) {
                if (e.target === modalOverlay) cerrarModal();
            });
        }

        // Cerrar panel / modal con Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') { cerrarModal(); cerrarPanel(); }
        });

        // Enviar reseña
        if (btnEnviar) btnEnviar.addEventListener('click', enviarResena);
    });

})();
