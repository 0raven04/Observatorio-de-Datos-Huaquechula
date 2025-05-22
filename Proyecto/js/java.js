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