document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function () {
        const isDesktop = window.innerWidth >= 768;

        if (isDesktop && window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else if (isDesktop) {
            navbar.classList.remove('scrolled');
        }
    });

 
    window.addEventListener('resize', () => {
        if (window.innerWidth < 768) {
            navbar.classList.remove('scrolled');
        }
    });
});

window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
      navbar.classList.add('navbar-scrolled');
    } else {
      navbar.classList.remove('navbar-scrolled');
    }
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
        });