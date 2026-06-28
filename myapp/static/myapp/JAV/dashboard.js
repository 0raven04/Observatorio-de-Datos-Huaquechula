/**
 * Dashboard — Observatorio Territorial Huaquechula
 * Interactive visualization logic
 */

(function () {
    'use strict';

    // ── Chart.js Global Defaults ─────────────────────
    if (window.Chart) {
        Chart.defaults.font.family = "'Inter', 'Segoe UI', system-ui, sans-serif";
        Chart.defaults.color = '#5D6D7E';
        Chart.defaults.plugins.legend.display = false;
        Chart.defaults.animation.duration = 800;
        Chart.defaults.animation.easing = 'easeOutQuart';
    }

    // ── Color Palette ────────────────────────────────
    const COLORS = {
        naranja: '#E67E22',
        naranjaDark: '#D35400',
        naranjaLight: 'rgba(230, 126, 34, 0.15)',
        bienestar: '#2980B9',
        tradicion: '#8E44AD',
        turismo: '#27AE60',
        success: '#27AE60',
        danger: '#E74C3C',
        gris: '#5D6D7E',
        grisOscuro: '#2C3E50',
        arena: '#E8DCC8',

        chartPalette: [
            '#E67E22', '#2980B9', '#27AE60', '#8E44AD',
            '#E74C3C', '#F39C12', '#1ABC9C', '#34495E'
        ],

        gradient(ctx, color, height) {
            const gradient = ctx.createLinearGradient(0, 0, 0, height || 300);
            gradient.addColorStop(0, color.replace(')', ', 0.3)').replace('rgb', 'rgba'));
            gradient.addColorStop(1, color.replace(')', ', 0.02)').replace('rgb', 'rgba'));
            return gradient;
        }
    };

    // ── Utility: Determine chart type by unit ────────
    function getChartTypeForUnit(unit) {
        const u = (unit || '').toLowerCase();
        if (u.includes('porcentaje') || u.includes('%')) return 'doughnut';
        if (u.includes('índice') || u.includes('indice')) return 'radar';
        if (u.includes('personas') || u.includes('cantidad') || u.includes('por 100')) return 'bar';
        return 'line'; // default: Años, Pesos, Promedio, etc.
    }

    // ── Utility: Trend calculation ───────────────────
    function calcTrend(values) {
        if (!values || values.length < 2) return { direction: 'stable', percent: 0 };
        const last = values[values.length - 1];
        const prev = values[values.length - 2];
        if (prev === 0) return { direction: 'stable', percent: 0 };
        const change = ((last - prev) / Math.abs(prev)) * 100;
        return {
            direction: change > 0.5 ? 'up' : change < -0.5 ? 'down' : 'stable',
            percent: Math.abs(change).toFixed(1)
        };
    }

    // ── Counter Animation ────────────────────────────
    function animateCounter(element, target, duration) {
        duration = duration || 1200;
        const isDecimal = target % 1 !== 0;
        const start = 0;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // easeOutExpo
            const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            const current = start + (target - start) * eased;

            if (target >= 10000) {
                element.textContent = Math.round(current).toLocaleString('es-MX');
            } else if (isDecimal) {
                element.textContent = current.toFixed(1);
            } else {
                element.textContent = Math.round(current).toLocaleString('es-MX');
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }

    // ── Mini Sparkline ───────────────────────────────
    function createSparkline(canvas, values, color) {
        if (!canvas || !values || values.length === 0) return null;
        color = color || COLORS.naranja;

        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: values.map((_, i) => ''),
                datasets: [{
                    data: values,
                    borderColor: color,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: color,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: function(context) {
                        const chart = context.chart;
                        const {ctx: c, chartArea} = chart;
                        if (!chartArea) return color;
                        const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                        gradient.addColorStop(0, color.replace(')', ',0.2)').replace('rgb', 'rgba').replace('#', ''));
                        // Simple fallback for hex colors
                        gradient.addColorStop(0, hexToRgba(color, 0.2));
                        gradient.addColorStop(1, hexToRgba(color, 0.0));
                        return gradient;
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                interaction: { mode: 'index', intersect: false },
                elements: { line: { borderJoinStyle: 'round' } }
            }
        });
    }

    function hexToRgba(hex, alpha) {
        hex = hex.replace('#', '');
        if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // ── Sidebar Filtering ────────────────────────────
    function initSidebar() {
        const navItems = document.querySelectorAll('.sidebar-nav-item');
        const axisSections = document.querySelectorAll('.axis-section');

        navItems.forEach(item => {
            item.addEventListener('click', function (e) {
                e.preventDefault();
                navItems.forEach(n => n.classList.remove('active'));
                this.classList.add('active');

                // Toggle sub-nav if it's a group
                const group = this.closest('.sidebar-nav-group');
                if (group) {
                    const wasActive = group.classList.contains('active');
                    document.querySelectorAll('.sidebar-nav-group').forEach(g => g.classList.remove('active'));
                    // Close all category sub-menus when switching eje
                    document.querySelectorAll('.sidebar-sub-nav-item').forEach(b => b.classList.remove('cat-active'));
                    document.querySelectorAll('.sidebar-indicator-nav').forEach(n => n.classList.remove('ind-active'));
                    if (!wasActive) {
                        group.classList.add('active');
                    }
                } else {
                    // "Todas las dimensiones" — close all groups
                    document.querySelectorAll('.sidebar-nav-group').forEach(g => g.classList.remove('active'));
                    document.querySelectorAll('.sidebar-sub-nav-item').forEach(b => b.classList.remove('cat-active'));
                    document.querySelectorAll('.sidebar-indicator-nav').forEach(n => n.classList.remove('ind-active'));
                }

                const filter = group ? group.getAttribute('data-filter') : this.getAttribute('data-filter');
                axisSections.forEach(section => {
                    if (filter === 'all' || section.getAttribute('data-eje') === filter) {
                        section.style.display = '';
                        section.style.animation = 'fadeInUp 0.4s ease-out both';
                    } else {
                        section.style.display = 'none';
                    }
                });
            });
        });

        // ── Category toggle (2nd level → 3rd level) ──
        document.querySelectorAll('.sidebar-sub-nav-item[data-cat-id]').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.stopPropagation(); // no activar el eje padre
                const catId = this.getAttribute('data-cat-id');
                const indNav = document.getElementById('ind-nav-' + catId);
                const wasActive = this.classList.contains('cat-active');

                // Cerrar todos los submenús de indicadores en el mismo grupo
                const parentSubNav = this.closest('.sidebar-sub-nav');
                if (parentSubNav) {
                    parentSubNav.querySelectorAll('.sidebar-sub-nav-item').forEach(b => b.classList.remove('cat-active'));
                    parentSubNav.querySelectorAll('.sidebar-indicator-nav').forEach(n => n.classList.remove('ind-active'));
                }

                if (!wasActive && indNav) {
                    this.classList.add('cat-active');
                    indNav.classList.add('ind-active');

                    // Scroll suave al bloque de la categoría en el contenido
                    const catBlock = document.getElementById('cat-' + catId);
                    if (catBlock) {
                        catBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
        });

        // ── Indicator click (3rd level → scroll + highlight) ──
        document.querySelectorAll('.sidebar-indicator-item[data-indicator-id]').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const indId = this.getAttribute('data-indicator-id');
                const card = document.getElementById('indicator-' + indId);
                if (!card) return;

                // Asegurarse de que la sección del eje esté visible
                const section = card.closest('.axis-section');
                if (section && section.style.display === 'none') {
                    axisSections.forEach(s => s.style.display = '');
                }

                // Pre-forzar animate-in para evitar conflicto con IntersectionObserver
                card.classList.add('animate-in');

                // Scroll suave a la tarjeta
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Esperar a que el scroll termine (~600ms) antes de animar
                setTimeout(() => {
                    // Limpiar animación previa si existiera
                    card.classList.remove('highlighted');
                    void card.offsetWidth; // reflow para reiniciar

                    // Usar animationend para limpiar la clase exactamente al terminar
                    function onHighlightEnd() {
                        card.classList.remove('highlighted');
                        card.removeEventListener('animationend', onHighlightEnd);
                    }
                    card.addEventListener('animationend', onHighlightEnd);
                    card.classList.add('highlighted');
                }, 600);
            });
        });
    }

    // ── KPI Counter Init ─────────────────────────────
    function initKPICounters() {
        const kpiValues = document.querySelectorAll('.kpi-value[data-target]');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseFloat(el.getAttribute('data-target'));
                    animateCounter(el, target);
                    observer.unobserve(el);
                }
            });
        }, { threshold: 0.5 });

        kpiValues.forEach(el => observer.observe(el));
    }

    // ── Sparklines Init ──────────────────────────────
    function initSparklines() {
        document.querySelectorAll('.indicator-sparkline canvas').forEach(canvas => {
            const rawData = canvas.getAttribute('data-values');
            const color = canvas.getAttribute('data-color') || COLORS.naranja;
            if (rawData) {
                try {
                    const values = JSON.parse(rawData);
                    if (values.length > 0) {
                        createSparkline(canvas, values, color);
                    }
                } catch (e) {
                    // skip invalid data
                }
            }
        });
    }

    // ── Main Chart Modal ─────────────────────────────
    let currentChart = null;
    let currentChartData = null;

    window.showIndicatorChart = function (indicatorId, indicatorName) {
        const modalEl = document.getElementById('chartModal');
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();

        const skeletonEl = document.getElementById('chartModalSkeleton');
        const contentEl = document.getElementById('chartModalContent');
        const titleEl = document.getElementById('chartModalLabel');

        if (skeletonEl && contentEl) {
            skeletonEl.classList.add('active');
            contentEl.style.display = 'none';
        }

        titleEl.innerHTML = '<i class="fas fa-chart-line me-2"></i>' + indicatorName;

        fetch('/api/indicator/' + indicatorId + '/chart-data/')
            .then(function (r) {
                if (!r.ok) throw new Error('Error');
                return r.json();
            })
            .then(function (data) {
                currentChartData = data;
                const suggestedType = getChartTypeForUnit(data.unit);
                renderMainChart(data, suggestedType);
                updateChartTypeSwitcher(suggestedType);
                renderMetadata(data);
                
                if (skeletonEl && contentEl) {
                    setTimeout(() => {
                        skeletonEl.classList.remove('active');
                        contentEl.style.display = 'block';
                    }, 400); // slight delay to ensure smooth transition
                }
            })
            .catch(function () {
                if (skeletonEl && contentEl) {
                    skeletonEl.classList.remove('active');
                    contentEl.style.display = 'block';
                }
                const metadataEl = document.getElementById('chartMetadata');
                if(metadataEl) metadataEl.innerHTML = '<div class="text-center text-danger py-3"><i class="fas fa-exclamation-triangle me-2"></i>Error al cargar datos</div>';
            });
    };

    function renderMainChart(data, chartType) {
        if (currentChart) currentChart.destroy();

        const ctx = document.getElementById('mainChartCanvas').getContext('2d');
        const color = COLORS.naranja;
        const config = buildChartConfig(data, chartType, ctx);
        currentChart = new Chart(ctx, config);
    }

    function buildChartConfig(data, type, ctx) {
        const baseDataset = {
            label: data.indicator_name,
            data: data.values,
        };

        switch (type) {
            case 'bar':
                return {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            ...baseDataset,
                            backgroundColor: data.labels.map((_, i) => COLORS.chartPalette[i % COLORS.chartPalette.length]),
                            borderRadius: 6,
                            borderSkipped: false,
                            maxBarThickness: 60
                        }]
                    },
                    options: chartOptions(data, 'bar')
                };

            case 'doughnut':
                return {
                    type: 'doughnut',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            ...baseDataset,
                            backgroundColor: data.labels.map((_, i) => COLORS.chartPalette[i % COLORS.chartPalette.length]),
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        cutout: '65%',
                        plugins: {
                            legend: { display: true, position: 'bottom' },
                            tooltip: tooltipConfig(data)
                        }
                    }
                };

            case 'radar':
                return {
                    type: 'radar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            ...baseDataset,
                            backgroundColor: hexToRgba(COLORS.naranja, 0.2),
                            borderColor: COLORS.naranja,
                            borderWidth: 2,
                            pointBackgroundColor: COLORS.naranja,
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: { display: false },
                            tooltip: tooltipConfig(data)
                        },
                        scales: {
                            r: {
                                beginAtZero: true,
                                grid: { color: 'rgba(0,0,0,0.05)' },
                                angleLines: { color: 'rgba(0,0,0,0.05)' }
                            }
                        }
                    }
                };

            default: // line
                return {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            ...baseDataset,
                            borderColor: COLORS.naranja,
                            backgroundColor: hexToRgba(COLORS.naranja, 0.08),
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 5,
                            pointHoverRadius: 8,
                            pointBackgroundColor: COLORS.naranja,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointHoverBorderWidth: 3
                        }]
                    },
                    options: chartOptions(data, 'line')
                };
        }
    }

    function chartOptions(data, type) {
        return {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: tooltipConfig(data)
            },
            scales: {
                y: {
                    beginAtZero: type === 'bar',
                    title: {
                        display: true,
                        text: data.unit || '',
                        font: { size: 12, weight: '600' },
                        color: '#5D6D7E'
                    },
                    grid: { color: 'rgba(0,0,0,0.04)' },
                    ticks: { font: { size: 11 } }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Período',
                        font: { size: 12, weight: '600' },
                        color: '#5D6D7E'
                    },
                    grid: { display: false },
                    ticks: { font: { size: 11 } }
                }
            }
        };
    }

    function tooltipConfig(data) {
        return {
            backgroundColor: 'rgba(44, 62, 80, 0.95)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: COLORS.naranja,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
                label: function (context) {
                    return context.parsed.y !== undefined
                        ? context.parsed.y.toLocaleString('es-MX') + ' ' + (data.unit || '')
                        : context.parsed + ' ' + (data.unit || '');
                }
            }
        };
    }

    function updateChartTypeSwitcher(activeType) {
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-type') === activeType);
        });
    }

    function renderMetadata(data) {
        const el = document.getElementById('chartMetadata');
        const trend = calcTrend(data.values);
        const trendIcon = trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : '→';
        const trendClass = trend.direction;

        // Data source badge
        var sourceIsInegi = data.data_source === 'inegi';
        var sourceBadge = sourceIsInegi
            ? '<span class="indicator-source-badge inegi" style="font-size:0.75rem;padding:4px 10px;"><i class="fas fa-university me-1"></i>INEGI</span>'
            : '<span class="indicator-source-badge local" style="font-size:0.75rem;padding:4px 10px;"><i class="fas fa-map-marker-alt me-1"></i>LOCAL</span>';
        var inegiLine = (sourceIsInegi && data.inegi_id)
            ? '<div style="font-size:0.75rem;color:var(--color-gris-claro);margin-top:2px;">ID INEGI: ' + data.inegi_id + '</div>'
            : '';

        el.innerHTML =
            '<div class="chart-metadata-grid">' +
                '<div class="chart-meta-item"><label>Eje</label><span>' + (data.axis || '-') + '</span></div>' +
                '<div class="chart-meta-item"><label>Categoría</label><span>' + (data.category || '-') + '</span></div>' +
                '<div class="chart-meta-item"><label>Unidad</label><span>' + (data.unit || '-') + '</span></div>' +
                '<div class="chart-meta-item"><label>Última act.</label><span>' + (data.last_updated || 'Sin datos') + '</span></div>' +
                '<div class="chart-meta-item"><label>Fuente de datos</label><div>' + sourceBadge + inegiLine + '</div></div>' +
            '</div>' +
            // Source description row
            '<div style="margin-top:12px;padding:10px 14px;background:' + (sourceIsInegi ? 'rgba(41,128,185,0.06)' : 'rgba(39,174,96,0.06)') + ';border-radius:8px;border-left:3px solid ' + (sourceIsInegi ? 'var(--eje-bienestar)' : 'var(--eje-turismo)') + ';">' +
                '<div style="display:flex;align-items:center;gap:8px;">' +
                    '<i class="fas ' + (sourceIsInegi ? 'fa-database' : 'fa-clipboard-list') + '" style="color:' + (sourceIsInegi ? 'var(--eje-bienestar)' : 'var(--eje-turismo)') + ';"></i>' +
                    '<div>' +
                        '<div style="font-size:0.8rem;font-weight:600;color:var(--color-gris-oscuro);">' + (data.data_source_label || 'Fuente no especificada') + '</div>' +
                        (data.description ? '<div style="font-size:0.75rem;color:var(--color-gris-medio);margin-top:2px;">' + data.description + '</div>' : '') +
                    '</div>' +
                '</div>' +
            '</div>' +
            // Bottom row: period count + trend
            '<div class="d-flex justify-content-between align-items-center mt-3">' +
                '<small class="text-muted"><i class="fas fa-chart-bar me-1"></i>' + data.labels.length + ' período(s) de datos</small>' +
                '<span class="indicator-trend ' + trendClass + '">' + trendIcon + ' ' + trend.percent + '%</span>' +
            '</div>';
    }

    // Chart type switcher handler
    window.switchChartType = function (type) {
        if (currentChartData) {
            renderMainChart(currentChartData, type);
            updateChartTypeSwitcher(type);
        }
    };

    // ── PDF Download ─────────────────────────────────
    window.downloadChartPDF = function () {
        if (!currentChartData || !window.jspdf) return;

        var data = currentChartData;
        var jsPDF = window.jspdf.jsPDF;
        var doc = new jsPDF('landscape', 'mm', 'a4');
        var pageW = doc.internal.pageSize.getWidth();
        var pageH = doc.internal.pageSize.getHeight();
        var margin = 15;

        // ── Header bar ──────────────────────────────
        doc.setFillColor(44, 62, 80);
        doc.rect(0, 0, pageW, 22, 'F');
        doc.setFontSize(14);
        doc.setTextColor(255, 255, 255);
        doc.text('Observatorio Territorial de Huaquechula', margin, 14);
        doc.setFontSize(9);
        doc.text('Reporte generado: ' + new Date().toLocaleDateString('es-MX', { year:'numeric', month:'long', day:'numeric' }), pageW - margin, 14, { align: 'right' });

        // ── Indicator title ─────────────────────────
        var yPos = 32;
        doc.setTextColor(44, 62, 80);
        doc.setFontSize(16);
        doc.text(data.indicator_name, margin, yPos);
        yPos += 8;

        // ── Metadata line ───────────────────────────
        doc.setFontSize(9);
        doc.setTextColor(93, 109, 126);
        doc.text('Eje: ' + (data.axis || '-') + '   |   Categoría: ' + (data.category || '-') + '   |   Unidad: ' + (data.unit || '-'), margin, yPos);
        doc.text('Última actualización: ' + (data.last_updated || 'Sin datos'), pageW - margin, yPos, { align: 'right' });
        yPos += 10;

        // ── Chart image ─────────────────────────────
        var canvas = document.getElementById('mainChartCanvas');
        if (canvas) {
            var imgData = canvas.toDataURL('image/png', 1.0);
            var chartW = pageW - margin * 2;
            var chartH = chartW * 0.45;
            if (yPos + chartH > pageH - 50) chartH = pageH - yPos - 55;
            doc.addImage(imgData, 'PNG', margin, yPos, chartW, chartH);
            yPos += chartH + 8;
        }

        // ── Data table ──────────────────────────────
        if (data.labels && data.labels.length > 0) {
            doc.setFontSize(10);
            doc.setTextColor(44, 62, 80);
            doc.text('Datos Históricos', margin, yPos);
            yPos += 6;

            // Table header
            var colW = Math.min(30, (pageW - margin * 2) / data.labels.length);
            doc.setFillColor(232, 220, 200);
            doc.setDrawColor(200, 200, 200);
            for (var i = 0; i < data.labels.length; i++) {
                var x = margin + i * colW;
                doc.rect(x, yPos, colW, 7, 'FD');
                doc.setFontSize(8);
                doc.setTextColor(44, 62, 80);
                doc.text(data.labels[i], x + colW / 2, yPos + 5, { align: 'center' });
            }
            yPos += 7;

            // Table values
            for (var j = 0; j < data.values.length; j++) {
                var xv = margin + j * colW;
                doc.rect(xv, yPos, colW, 7, 'D');
                doc.setFontSize(8);
                doc.setTextColor(93, 109, 126);
                var valStr = data.values[j] % 1 === 0 ? data.values[j].toLocaleString('es-MX') : data.values[j].toFixed(2);
                doc.text(valStr, xv + colW / 2, yPos + 5, { align: 'center' });
            }
            yPos += 12;
        }

        // ── Source info ─────────────────────────────
        doc.setFontSize(9);
        doc.setTextColor(93, 109, 126);
        var srcIcon = data.data_source === 'inegi' ? '[INEGI]' : '[LOCAL]';
        doc.text('Fuente: ' + srcIcon + ' ' + (data.data_source_label || ''), margin, yPos);
        if (data.inegi_id) {
            yPos += 5;
            doc.text('ID Indicador INEGI: ' + data.inegi_id, margin, yPos);
        }

        // ── Footer bar ──────────────────────────────
        doc.setFillColor(44, 62, 80);
        doc.rect(0, pageH - 10, pageW, 10, 'F');
        doc.setFontSize(7);
        doc.setTextColor(180, 180, 180);
        doc.text('© 2025 Observatorio Turístico de Huaquechula', pageW / 2, pageH - 4, { align: 'center' });

        // ── Save ─────────────────────────────────────
        var safeName = data.indicator_name.replace(/[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ ]/g, '').replace(/\s+/g, '_');
        doc.save('indicador_' + safeName + '.pdf');
    };

    // ── Scroll-based animations ──────────────────────
    function initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

        document.querySelectorAll('.indicator-card, .category-block').forEach(el => {
            observer.observe(el);
        });
    }

    // ── View Toggle (Grid / List) ────────────────────
    function initViewToggle() {
        const btns = document.querySelectorAll('.view-toggle-btn');
        const grids = document.querySelectorAll('.indicators-grid');
        if (btns.length === 0) return;

        // Load preference
        const savedView = localStorage.getItem('huaquechula_dashboard_view') || 'grid';
        applyView(savedView);

        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.getAttribute('data-view');
                applyView(view);
                localStorage.setItem('huaquechula_dashboard_view', view);
            });
        });

        function applyView(view) {
            btns.forEach(b => b.classList.toggle('active', b.getAttribute('data-view') === view));
            grids.forEach(grid => {
                if (view === 'list') {
                    grid.classList.add('list-view');
                } else {
                    grid.classList.remove('list-view');
                }
            });
        }
    }

    // ── Indicator Info Tooltips ──────────────────────
    const INDICATOR_DETAILS = {
        // Bienestar Social / Salud
        "esperanza de vida al nacer": {
            desc: "Número promedio de años que se espera que viva un recién nacido si se mantienen las tasas de mortalidad por edad de ese año.",
            inputs: "Registros de defunciones, actas de nacimiento y proyecciones de población."
        },
        "esperanza de vida": {
            desc: "Número promedio de años que se espera que viva un recién nacido si se mantienen las tasas de mortalidad por edad de ese año.",
            inputs: "Registros de defunciones, actas de nacimiento y proyecciones de población."
        },
        "salud autorreportada": {
            desc: "Indicador subjetivo que mide cómo perciben los individuos su propio estado de salud (excelente, bueno, regular, malo).",
            inputs: "Encuestas de hogares o de salud (preguntas de percepción)."
        },
        "tasa de obesidad": {
            desc: "Porcentaje de la población con un Índice de Masa Corporal (IMC >= 30). Mide riesgos de salud pública.",
            inputs: "Peso y talla de la población muestreada (o autoreportada) y total de población."
        },
        "tasa de mortalidad": {
            desc: "Número de defunciones por cada 1,000 habitantes en un año determinado.",
            inputs: "Número total de muertes en un año y población total a mitad de año."
        },
        "tasa de mortalidad infantil": {
            desc: "Número de defunciones por cada 1,000 habitantes en un año determinado.",
            inputs: "Número total de muertes en un año y población total a mitad de año."
        },
        "razón de mortalidad materna": {
            desc: "Número de muertes de mujeres durante el embarazo, parto o puerperio por cada 100,000 nacidos vivos.",
            inputs: "Registro de muertes maternas y total de nacidos vivos en el mismo periodo."
        },
        // Bienestar Social / Accesibilidad a servicios
        "acceso a servicios de salud": {
            desc: "Porcentaje de la población que cuenta con adscripción o derecho a recibir servicios médicos (públicos o privados).",
            inputs: "Encuestas de ingresos/gastos o censos (afiliación a instituciones de salud)."
        },
        "acceso a servicios de banda ancha": {
            desc: "Porcentaje de hogares o contratos de internet de alta velocidad en una región respecto al total.",
            inputs: "Contratos de telecomunicaciones o encuestas de disponibilidad de TIC en hogares."
        },
        "acceso a los servicios de banda ancha": {
            desc: "Porcentaje de hogares o contratos de internet de alta velocidad en una región respecto al total.",
            inputs: "Contratos de telecomunicaciones o encuestas de disponibilidad de TIC en hogares."
        },
        "vivienda con acceso a servicios básicos": {
            desc: "Porcentaje de viviendas que cuentan con agua entubada, drenaje, electricidad y eliminación de basura.",
            inputs: "Censo de vivienda o encuestas de condiciones socioeconómicas."
        },
        "vivienda con acceso de servicios básicos": {
            desc: "Porcentaje de viviendas que cuentan con agua entubada, drenaje, electricidad y eliminación de basura.",
            inputs: "Censo de vivienda o encuestas de condiciones socioeconómicas."
        },
        // Bienestar Social / Educación
        "niveles de educación": {
            desc: "Distribución porcentual de la población según el máximo nivel educativo alcanzado (primaria, secundaria, superior, etc.).",
            inputs: "Censos de población o encuestas de hogares (último grado aprobado)."
        },
        "deserción escolar": {
            desc: "Porcentaje de alumnos que abandonan las aulas de un ciclo escolar a otro, antes de concluir el nivel educativo.",
            inputs: "Matrícula inicial, matrícula final y egresados por nivel educativo (registros escolares)."
        },
        "años promedio de escolaridad": {
            desc: "Número medio de años de educación formal completados por la población de una determinada edad (ej. mayores de 15 años).",
            inputs: "Edad de la población y el último año/grado escolar aprobado."
        },
        "grado promedio de escolaridad": {
            desc: "Número medio de años de educación formal completados por la población de una determinada edad (ej. mayores de 15 años).",
            inputs: "Edad de la población y el último año/grado escolar aprobado."
        },
        // Bienestar Social / Vivienda
        "habitaciones por persona": {
            desc: "Promedio de cuartos disponibles en la vivienda por cada habitante (mide el nivel de hacinamiento).",
            inputs: "Número total de habitaciones en la vivienda (excluyendo baños/cocinas según metodología) y número de residentes."
        },
        "viviendas con techos de materiales resistentes": {
            desc: "Porcentaje de viviendas cuyos techos están construidos con materiales durables (losa de concreto, vigueta, etc.) y no precarios.",
            inputs: "Datos del censo de vivienda sobre características físicas de los materiales de construcción."
        },
        // Bienestar Social / Ingresos / Pobreza
        "gini del ingreso disponible de los hogares per cápita": {
            desc: "Medida de desigualdad económica (de 0 a 1, donde 1 es desigualdad máxima) basada en los ingresos netos por integrante del hogar.",
            inputs: "Ingresos de todos los miembros del hogar (salarios, transferencias, remesas) menos impuestos, y tamaño del hogar."
        },
        "ingreso equivalente disponible de los hogares": {
            desc: "Ingreso total del hogar ajustado por el tamaño y composición del hogar (economías de escala) para hacerlos comparables.",
            inputs: "Ingreso neto del hogar y escala de equivalencia (ej. escala de la OCDE que pondera adultos y niños)."
        },
        "población en pobreza": {
            desc: "Porcentaje de personas cuyos ingresos están por debajo de la línea de pobreza y/o presentan carencias sociales.",
            inputs: "Ingresos del hogar, líneas de canasta básica y datos de acceso a derechos sociales."
        },
        "población en pobreza extrema": {
            desc: "Porcentaje de personas que no disponen de ingresos suficientes ni para adquirir la canasta alimentaria básica y tienen múltiples carencias.",
            inputs: "Ingreso del hogar y costo de la canasta alimentaria (línea de pobreza extrema)."
        },
        // Bienestar Social / Empleo
        "tasa de condiciones críticas de ocupación": {
            desc: "Porcentaje de la población ocupada que trabaja menos de 35 horas por razones de mercado, o gana menos del salario mínimo trabajando mucho.",
            inputs: "Encuestas de empleo (horas trabajadas e ingresos laborales)."
        },
        "informalidad laboral": {
            desc: "Porcentaje de la población ocupada que carece de seguridad social y cuyas unidades económicas no están registradas.",
            inputs: "Encuestas de empleo (estatus de contratación y acceso a seguridad social)."
        },
        "tasa de desocupación": {
            desc: "Porcentaje de la Población Económicamente Activa (PEA) que no tiene empleo pero está buscando activamente uno.",
            inputs: "Número de personas desocupadas y total de la PEA."
        },
        "participación económica": {
            desc: "Porcentaje de la población en edad de trabajar (ej. 15 años o más) que está empleada o buscando empleo (PEA).",
            inputs: "Población Económicamente Activa y Población en Edad de Trabajar (PET)."
        },
        // Bienestar Social / Seguridad
        "tasa de homicidios": {
            desc: "Número de muertes por homicidio intencional por cada 100,000 habitantes.",
            inputs: "Registros forenses, carpetas de investigación judicial y población total."
        },
        "confianza policía": {
            desc: "Porcentaje de la población que manifiesta tener 'mucha' o 'algo' de confianza en los cuerpos policiales locales o estatales.",
            inputs: "Encuestas de victimización y percepción de seguridad pública."
        },
        "confianza en la policía": {
            desc: "Porcentaje de la población que manifiesta tener 'mucha' o 'algo' de confianza en los cuerpos policiales locales o estatales.",
            inputs: "Encuestas de victimización y percepción de seguridad pública."
        },
        "percepción de inseguridad": {
            desc: "Porcentaje de la población que se siente insegura viviendo en su ciudad, municipio o colonia.",
            inputs: "Encuestas de opinión/percepción ciudadana sobre seguridad."
        },
        "incidencia delictiva": {
            desc: "Número de delitos denunciados o estimados ocurridos por cada 100,000 habitantes.",
            inputs: "Denuncias registradas ante fiscalías y encuestas de victimización (para calcular la cifra negra)."
        },
        // Bienestar Social / Medio Ambiente
        "contaminación del aire": {
            desc: "Concentración de partículas suspendidas (PM2.5, PM10) y gases del efecto invernadero en la atmósfera local.",
            inputs: "Datos de estaciones de monitoreo ambiental y sensores de calidad del aire."
        },
        "disposición de residuos": {
            desc: "Porcentaje de residuos sólidos recolectados que son destinados a sitios autorizados (rellenos sanitarios) vs. basureros a cielo abierto.",
            inputs: "Registros municipales de recolección y pesaje de basura."
        },
        "alternativas de gestión comunitaria de medio ambiente": {
            desc: "Número o porcentaje de iniciativas locales (comunales, ejidales) orientadas al reciclaje, reforestación o conservación de recursos.",
            inputs: "Registros de proyectos locales, actas ejidales o padrón de ONGs ambientales."
        },
        // Bienestar Social / Migración
        "índice de intensidad migratoria": {
            desc: "Medida multidimensional que evalúa el flujo de personas que salen o entran a una localidad (remesas, emigrantes, circulares).",
            inputs: "Datos censales sobre lugar de residencia anterior, recepción de remesas y migración internacional en los hogares."
        },
        // Indicadores de Impacto Comunitario y Tradición (PCI)
        "tensión sobre la población local": {
            desc: "Nivel de estrés o fricción socioeconómica (gentrificación, encarecimiento, ruido) percibido por los residentes debido al turismo masivo.",
            inputs: "Encuestas a residentes locales y análisis de precios de rentas/productos."
        },
        "acceso de la población a los servicios públicos durante la tradición": {
            desc: "Evaluación de si la infraestructura pública (agua, transporte, luz) falla o se satura para los locales durante festividades o eventos.",
            inputs: "Reportes de fallas de servicios públicos y encuestas a vecinos durante fechas festivas."
        },
        "tensiones físicas y simbólicas sobre la tradición": {
            desc: "Grado de alteración, mercantilización o pérdida de significado de una tradición debido a la llegada de externos.",
            inputs: "Entrevistas cualitativas a portadores de la tradición, líderes comunitarios y observaciones."
        },
        "procesos de salvaguardia del patrimonio": {
            desc: "Existencia y nivel de ejecución de planes y leyes dedicadas a proteger el Patrimonio Cultural Inmaterial (PCI).",
            inputs: "Documentos jurídicos, presupuestos asignados a cultura y actas de comités de salvaguardia."
        },
        "seguimiento de salvaguardia": {
            desc: "Monitoreo continuo y evaluación del impacto de las acciones aplicadas para proteger el patrimonio.",
            inputs: "Informes técnicos anuales, auditorías culturales e indicadores de efectividad."
        },
        "seguimiento a la salvaguardia": {
            desc: "Monitoreo continuo y evaluación del impacto de las acciones aplicadas para proteger el patrimonio.",
            inputs: "Informes técnicos anuales, auditorías culturales e indicadores de efectividad."
        },
        "difusión de pci": {
            desc: "Cantidad de campañas, talleres o medios digitales/impresos enfocados en educar sobre el Patrimonio Cultural Inmaterial.",
            inputs: "Presupuesto publicitario, número de eventos de difusión y alcance en redes o medios."
        },
        "relación comunidad - pci": {
            desc: "Nivel de apropiación, orgullo e identidad que siente la comunidad local respecto a su patrimonio inmaterial.",
            inputs: "Encuestas de identidad cultural y conteo de participación local activa en la festividad."
        },
        // Indicadores de Gobernanza y Gestión Turística
        "participación de la comunidad en la toma de decisiones": {
            desc: "Grado de involucramiento de los ciudadanos locales en los comités u órganos que deciden el rumbo del turismo o la cultura local.",
            inputs: "Actas de asambleas, listas de asistencia a comités ciudadanos y encuestas de participación."
        },
        "capacitación, información y comunicación": {
            desc: "Número de talleres impartidos y efectividad de los canales de información hacia los prestadores de servicios y comunidad.",
            inputs: "Registros de asistencia a cursos, encuestas de salida de capacitación y auditorías de comunicación."
        },
        "regulación": {
            desc: "Existencia y aplicación de normativas locales (bandos municipales, reglamentos de turismo) para controlar las actividades.",
            inputs: "Gacetas oficiales, leyes locales y número de inspecciones/sanciones aplicadas."
        },
        "herramientas de gestión": {
            desc: "Disponibilidad de planes de desarrollo turístico, manuales operativos, atlas de riesgo o software de control de visitantes.",
            inputs: "Inventario de documentos institucionales vigentes y herramientas tecnológicas en uso."
        },
        "proyectos turísticos": {
            desc: "Número y estado de desarrollo (planeados, en ejecución, terminados) de proyectos de infraestructura o productos turísticos.",
            inputs: "Carteras de inversión pública/privada y bitácoras de obra."
        },
        "integración territorial turística": {
            desc: "Medida en que los beneficios y rutas del turismo se conectan físicamente con otras zonas de la comunidad, evitando 'islas turísticas'.",
            inputs: "Mapas de rutas de transporte, dispersión de comercios locales y conectividad vial."
        },
        "integración turística territorial": {
            desc: "Medida en que los beneficios y rutas del turismo se conectan físicamente con otras zonas de la comunidad, evitando 'islas turísticas'.",
            inputs: "Mapas de rutas de transporte, dispersión de comercios locales y conectividad vial."
        },
        // Indicadores de Demanda y Perfil del Visitante
        "afluencia durante la tradición": {
            desc: "Número total de personas (turistas y excursionistas) que asisten específicamente a las fechas de la celebración tradicional.",
            inputs: "Conteo en puntos de acceso, ocupación hotelera en esos días y estimación de protección civil."
        },
        "visitantes anuales": {
            desc: "Volumen total de viajeros que recibe el destino a lo largo de todo un año calendario.",
            inputs: "Registros hoteleros (Datatur o similar), taquillas de atracciones y peajes."
        },
        "índice de satisfacción": {
            desc: "Evaluación porcentual o en escala del nivel de agrado del visitante respecto a su experiencia general en el destino.",
            inputs: "Encuestas aplicadas a los visitantes al momento de su salida del destino."
        },
        "afluencia por zonas": {
            desc: "Desglose del número de visitantes que acuden a puntos específicos de interés dentro del territorio (ej. centro histórico vs. periferia).",
            inputs: "Conteos en atractivos específicos, boletaje o mapas de calor mediante datos móviles."
        },
        "visitas por ciudad": {
            desc: "Registro del volumen de turistas distribuidos según su ciudad o región de origen (nacional o internacional).",
            inputs: "Libros de registro de hoteles, encuestas de perfil y bases de datos aeroportuarias/centrales de autobuses."
        },
        "perfil del visitante": {
            desc: "Características sociodemográficas del turista: edad, género, nivel de ingresos, ocupación, motivo del viaje.",
            inputs: "Encuestas de perfil del visitante aplicadas en zonas turísticas clave."
        },
        "grupo de visita": {
            desc: "Composición del grupo con el que viaja el turista (solo, en pareja, familia, amigos, excursión organizada).",
            inputs: "Encuestas de perfil (pregunta explícita sobre acompañantes y tamaño de grupo)."
        },
        "actividades populares": {
            desc: "Ranking de las actividades más realizadas por los turistas durante su estancia (comer, comprar artesanías, tours guiados).",
            inputs: "Cuestionarios sobre actividades realizadas durante el viaje."
        },
        "reseñas": {
            desc: "Análisis cualitativo y cuantitativo de los comentarios y calificaciones que dejan los usuarios en plataformas digitales.",
            inputs: "Raspado de datos (web scraping) o monitoreo de plataformas como TripAdvisor, Google Maps o Booking."
        }
    };

    function initIndicatorTooltips() {
        const names = document.querySelectorAll('.indicator-name');
        names.forEach(nameEl => {
            const rawName = nameEl.textContent.trim();
            const nameLower = rawName.toLowerCase();
            
            let details = INDICATOR_DETAILS[nameLower];
            if (!details) {
                // intentamos buscar una coincidencia de subcadena
                const matchingKey = Object.keys(INDICATOR_DETAILS).find(k => nameLower.includes(k) || k.includes(nameLower));
                if (matchingKey) {
                    details = INDICATOR_DETAILS[matchingKey];
                }
            }

            if (!details) {
                // Si no se encuentra en el diccionario, generamos una descripción por defecto según su contexto
                if (nameLower.includes("bienestar")) {
                    details = {
                        desc: "Medición del nivel de bienestar social y calidad de vida en el municipio.",
                        inputs: "Encuestas socioeconómicas municipales y estadísticas de desarrollo social."
                    };
                } else if (nameLower.includes("tradicion") || nameLower.includes("tradición") || nameLower.includes("patrimonio") || nameLower.includes("pci")) {
                    details = {
                        desc: "Evaluación y seguimiento de las tradiciones culturales y el patrimonio del municipio.",
                        inputs: "Registros de eventos culturales, encuestas de participación y salvaguardia comunitaria."
                    };
                } else if (nameLower.includes("turismo")) {
                    details = {
                        desc: "Seguimiento de la actividad y desarrollo del turismo comunitario en la región.",
                        inputs: "Registros de afluencia de visitantes y encuestas de satisfacción en zonas de interés."
                    };
                } else {
                    details = {
                        desc: "Indicador de monitoreo del desarrollo local e impacto territorial en el municipio de Huaquechula.",
                        inputs: "Registros administrativos locales e información estadística complementaria."
                    };
                }
            }


            if (details) {
                const tooltipContainer = document.createElement('div');
                tooltipContainer.className = 'info-tooltip-container';
                tooltipContainer.innerHTML = `
                    <i class="fas fa-info-circle info-tooltip-trigger"></i>
                    <div class="info-tooltip-box">
                        <div class="info-tooltip-title">
                            <i class="fas fa-info-circle me-1"></i> Metadatos
                        </div>
                        <div class="info-tooltip-section">
                            <span class="info-tooltip-label">Descripción</span>
                            <span class="info-tooltip-content">${details.desc}</span>
                        </div>
                        <div class="info-tooltip-section">
                            <span class="info-tooltip-label">Insumos Requeridos</span>
                            <span class="info-tooltip-content">${details.inputs}</span>
                        </div>
                    </div>
                `;
                // Evitamos la propagación del click al contenedor de la tarjeta (que abre el modal del gráfico)
                tooltipContainer.addEventListener('click', function (e) {
                    e.stopPropagation();
                });
                
                // Insertar dentro del elemento de nombre para no romper la estructura de grid en vista de lista
                nameEl.appendChild(tooltipContainer);

            }
        });
    }

    // ── Init ─────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        initSidebar();
        initKPICounters();
        initSparklines();
        initScrollAnimations();
        initViewToggle();
        initIndicatorTooltips();
    });
})();

