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
            '<div class="chart-metadata-grid" style="grid-template-columns:repeat(5,1fr);">' +
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

    // ── Init ─────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        initSidebar();
        initKPICounters();
        initSparklines();
        initScrollAnimations();
        initViewToggle();
    });
})();
