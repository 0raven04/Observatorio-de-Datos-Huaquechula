// Funcionalidad para el menú desplegable
document.addEventListener("DOMContentLoaded", function () {
    // Elementos del DOM
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.querySelector(".overlay");
    const indicatorContent = document.getElementById("indicator-content");
    const treeMenu = document.getElementById("treeMenu");
    let currentChart = null;

    // Datos de ejemplo para los indicadores
    const indicatorData = {
        "esperanza-vida": {
            title: "Esperanza de Vida al Nacer",
            description: "La esperanza de vida al nacer es un indicador que refleja el número promedio de años que se espera que viva una persona al nacer, basándose en las tasas de mortalidad por edad para un año específico.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Esperanza de Vida (años)",
                    data: [74.5, 75.2, 75.8, 76.3, 76.7, 77.1],
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.1,
                }],
            },
        },
        "salud-auto-reportada": {
            title: "Salud Auto Reportada",
            description: "Este indicador mide el porcentaje de la población que reporta su estado de salud como bueno o muy bueno.",
            type: "bar",
            data: {
                labels: ["Muy Bueno", "Bueno", "Regular", "Malo", "Muy Malo"],
                datasets: [{
                    label: "Porcentaje de Población",
                    data: [35, 40, 18, 5, 2],
                    backgroundColor: [
                        "rgba(75, 192, 192, 0.8)",
                        "rgba(54, 162, 235, 0.8)",
                        "rgba(255, 206, 86, 0.8)",
                        "rgba(255, 99, 132, 0.8)",
                        "rgba(153, 102, 255, 0.8)",
                    ],
                }],
            },
        },
        "obesidad": {
            title: "Tasa de Obesidad",
            description: "Porcentaje de la población adulta con índice de masa corporal (IMC) igual o superior a 30.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Tasa de Obesidad (%)",
                    data: [24.5, 26.1, 27.8, 29.3, 30.7, 32.1],
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    tension: 0.1,
                }],
            },
        },
        "mortalidad": {
            title: "Tasa de Mortalidad",
            description: "Número de muertes por cada 1,000 habitantes en un año determinado.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Tasa de Mortalidad (por 1000 hab.)",
                    data: [5.8, 5.6, 5.4, 5.3, 5.2, 5.1],
                    borderColor: "rgba(153, 102, 255, 1)",
                    backgroundColor: "rgba(153, 102, 255, 0.2)",
                    tension: 0.1,
                }],
            },
        },
        "mortalidad-materna": {
            title: "Razón de Mortalidad Materna",
            description: "Número de muertes maternas por cada 100,000 nacidos vivos.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Razón de Mortalidad Materna",
                    data: [55, 48, 42, 38, 34, 30],
                    borderColor: "rgba(255, 159, 64, 1)",
                    backgroundColor: "rgba(255, 159, 64, 0.2)",
                    tension: 0.1,
                }],
            },
        },
        "acceso-salud": {
            title: "Acceso a Servicios de Salud",
            description: "Porcentaje de la población con acceso a servicios de salud básicos.",
            type: "bar",
            data: {
                labels: ["2010", "2015", "2020"],
                datasets: [{
                    label: "Población con acceso (%)",
                    data: [78, 85, 92],
                    backgroundColor: "rgba(54, 162, 235, 0.8)",
                }],
            },
        },
        "niveles-educacion": {
            title: "Niveles de Educación",
            description: "Distribución de la población por nivel educativo alcanzado.",
            type: "doughnut",
            data: {
                labels: ["Sin educación", "Primaria", "Secundaria", "Superior"],
                datasets: [{
                    data: [5, 25, 40, 30],
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.8)",
                        "rgba(54, 162, 235, 0.8)",
                        "rgba(255, 206, 86, 0.8)",
                        "rgba(75, 192, 192, 0.8)",
                    ],
                }],
            },
        },
        "pobreza": {
            title: "Población en Pobreza",
            description: "Porcentaje de la población que vive por debajo del umbral de pobreza.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Población en pobreza (%)",
                    data: [46.2, 45.5, 43.4, 41.9, 40.6, 43.9],
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    tension: 0.1,
                }],
            },
        },
        "homicidios": {
            title: "Tasa de Homicidios",
            description: "Número de homicidios por cada 100,000 habitantes.",
            type: "bar",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "Tasa de homicidios (por 100,000 hab.)",
                    data: [22, 21.5, 20, 19.5, 19, 18.5],
                    backgroundColor: "rgba(255, 99, 132, 0.8)",
                }],
            },
        },
        "contaminacion-aire": {
            title: "Contaminación del Aire",
            description: "Niveles promedio de partículas PM2.5 en microgramos por metro cúbico.",
            type: "line",
            data: {
                labels: ["2010", "2012", "2014", "2016", "2018", "2020"],
                datasets: [{
                    label: "PM2.5 (μg/m³)",
                    data: [25, 24, 23, 22, 21, 20],
                    borderColor: "rgba(153, 102, 255, 1)",
                    backgroundColor: "rgba(153, 102, 255, 0.2)",
                    tension: 0.1,
                }],
            },
        },
    };

     // Función para mostrar un gráfico según el indicador seleccionado
    function showIndicator(indicatorId) {
        const indicator = indicatorData[indicatorId];

        if (!indicator) {
            indicatorContent.innerHTML = `
                <div class="card">
                    <h2 class="indicator-title">Indicador no disponible</h2>
                    <p class="indicator-description">Los datos para este indicador no están disponibles en este momento.</p>
                </div>
            `;
            return;
        }

        // Destruir el gráfico anterior si existe
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }

        // Crear el contenido del indicador
        indicatorContent.innerHTML = `
            <div class="card">
                <h2 class="indicator-title">${indicator.title}</h2>
                <p class="indicator-description">${indicator.description}</p>
                <div class="chart-container">
                    <canvas id="indicatorChart"></canvas>
                </div>
            </div>
        `;

        // Obtener el contexto del canvas
        const ctx = document.getElementById("indicatorChart").getContext("2d");

        // Crear el gráfico
        currentChart = new Chart(ctx, {
            type: indicator.type,
            data: indicator.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                    },
                    title: {
                        display: true,
                        text: indicator.title,
                    },
                },
            },
        });
    }

    // MANEJO ÚNICO DEL MENÚ DESPLEGABLE
    treeMenu.addEventListener('click', function(e) {
        const target = e.target;
        
        // Si se hace clic en un enlace con hijos
        if (target.matches('.has-children > a')) {
            e.preventDefault();
            e.stopPropagation();
            
            const parentLi = target.parentElement;
            const wasActive = parentLi.classList.contains('active');
            
            // Solo cerrar otros menús del mismo nivel (no todos)
            const siblings = Array.from(parentLi.parentElement.children);
            siblings.forEach(sibling => {
                if (sibling !== parentLi && sibling.classList.contains('has-children')) {
                    sibling.classList.remove('active');
                }
            });
            
            // Alternar el estado del menú clickeado
            parentLi.classList.toggle('active');
        }
        
        // Si se hace clic en un enlace de indicador
        if (target.matches('a[data-indicator]')) {
            e.preventDefault();
            const indicatorId = target.getAttribute('data-indicator');
            showIndicator(indicatorId);
            
            // Cerrar menú en móvil
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                if (overlay) overlay.classList.remove('active');
            }
        }
    });

    // Manejar el botón de toggle en móviles
    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
            overlay.classList.toggle("active");
        });

        // Cerrar menú al hacer clic en el overlay
        overlay.addEventListener("click", function () {
            sidebar.classList.remove("active");
            overlay.classList.remove("active");
        });
    }

    // Agregar funcionalidad a las tarjetas del dashboard
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Card clicked:', this.querySelector('h3').textContent);
        });
    });

    // Manejo de redimensionamiento de ventana
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
        }
    });
});