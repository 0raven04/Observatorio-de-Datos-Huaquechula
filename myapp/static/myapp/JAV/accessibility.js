/**
 * MÓDULO DE ACCESIBILIDAD GLOBAL
 * Sistema de cambio dinámico de tamaño de texto
 * Compatible con: Bootstrap, Leaflet, formularios, tablas y componentes personalizados
 * 
 * Uso: Incluir este archivo en base.html
 * <script src="{% static 'myapp/JAV/accessibility.js' %}" defer></script>
 */

class AccessibilityManager {
    constructor() {
        // Configuración de tamaños
        this.config = {
            minSize: 12,      // px mínimo
            normalSize: 16,   // px normal
            maxSize: 24,      // px máximo
            step: 2,          // incremento por click
            storageKey: 'observatorio_font_size'
        };

        // Variables CSS que se van a modificar
        this.cssVariables = {
            baseFontSize: '--font-size-base',
            smallFont: '--font-size-small',
            largeFont: '--font-size-large'
        };

        this.currentSize = this.config.normalSize;
        this.init();
    }

    /**
     * Inicializa el módulo
     */
    init() {
        // Cargar tamaño guardado
        this.loadSavedSize();
        
        // Aplicar tamaño inicial
        this.applyFontSize(this.currentSize);
        
        // Escuchar cambios desde otros tabs/ventanas
        window.addEventListener('storage', (e) => {
            if (e.key === this.config.storageKey) {
                this.currentSize = parseInt(e.newValue) || this.config.normalSize;
                this.applyFontSize(this.currentSize);
            }
        });

        console.log('✓ Módulo de Accesibilidad inicializado');
    }

    /**
     * Carga el tamaño guardado en localStorage
     */
    loadSavedSize() {
        const savedSize = localStorage.getItem(this.config.storageKey);
        if (savedSize) {
            const size = parseInt(savedSize);
            if (size >= this.config.minSize && size <= this.config.maxSize) {
                this.currentSize = size;
            }
        }
    }

    /**
     * Aplica el tamaño de fuente globalmente
     * @param {number} size - Tamaño en píxeles
     */
    applyFontSize(size) {
        // Validar rango
        size = Math.max(this.config.minSize, Math.min(size, this.config.maxSize));
        this.currentSize = size;

        // Calcular tamaños relacionados
        const smallSize = Math.max(this.config.minSize, size - 2);
        const largeSize = Math.min(this.config.maxSize, size + 2);

        // Aplicar variables CSS en :root
        const root = document.documentElement;
        root.style.setProperty(this.cssVariables.baseFontSize, size + 'px');
        root.style.setProperty(this.cssVariables.smallFont, smallSize + 'px');
        root.style.setProperty(this.cssVariables.largeFont, largeSize + 'px');

        // Aplicar a elementos específicos
        this.applyToElements(size);

        // Guardar en localStorage
        localStorage.setItem(this.config.storageKey, size.toString());

        // Disparar evento personalizado para que otros scripts lo usen
        window.dispatchEvent(new CustomEvent('accessibilityChange', {
            detail: { fontSize: size }
        }));

        // Actualizar UI de controles
        this.updateControlsUI(size);
    }

    /**
     * Aplica cambios a elementos específicos
     * @param {number} size - Tamaño en píxeles
     */
    applyToElements(size) {
        // Body
        document.body.style.fontSize = size + 'px';

        // Títulos con escalado proporcional
        const headings = {
            h1: size + 8,
            h2: size + 6,
            h3: size + 4,
            h4: size + 2,
            h5: size,
            h6: size - 2
        };

        Object.entries(headings).forEach(([tag, fontSize]) => {
            document.querySelectorAll(tag).forEach(el => {
                el.style.fontSize = Math.max(this.config.minSize, fontSize) + 'px';
            });
        });

        // Párrafos
        document.querySelectorAll('p').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Botones
        document.querySelectorAll('button, .btn, input[type="button"], input[type="submit"]').forEach(el => {
            el.style.fontSize = (size - 1) + 'px';
        });

        // Enlaces
        document.querySelectorAll('a').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Inputs y textareas
        document.querySelectorAll('input, textarea, select').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Tablas
        document.querySelectorAll('table, td, th').forEach(el => {
            el.style.fontSize = (size - 1) + 'px';
        });

        // Labels
        document.querySelectorAll('label').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Cards
        document.querySelectorAll('.card, .card-title, .card-text').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Elementos con clase "text-*"
        document.querySelectorAll('[class*="text-"]').forEach(el => {
            if (!el.style.fontSize) {
                el.style.fontSize = size + 'px';
            }
        });

        // Navbars
        document.querySelectorAll('.navbar, .nav-link, .navbar-brand').forEach(el => {
            el.style.fontSize = (size - 1) + 'px';
        });

        // Modales y offcanvas
        document.querySelectorAll('.modal, .offcanvas, .modal-title, .offcanvas-title').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Sidebar (si existe)
        document.querySelectorAll('[class*="sidebar"], [id*="sidebar"]').forEach(el => {
            el.style.fontSize = (size - 1) + 'px';
        });

        // Chat widget
        document.querySelectorAll('#chat-widget, #chat-messages, #chat-input, .msg-bot, .msg-user').forEach(el => {
            el.style.fontSize = size + 'px';
        });

        // Footer
        document.querySelectorAll('footer, .foter_leter').forEach(el => {
            el.style.fontSize = (size - 1) + 'px';
        });

        // Popups y tooltips de Leaflet
        this.updateLeafletPopups(size);
    }

    /**
     * Actualiza tamaño de popups de Leaflet
     * @param {number} size - Tamaño en píxeles
     */
    updateLeafletPopups(size) {
        // Leaflet popup content
        document.querySelectorAll('.leaflet-popup-content, .leaflet-popup-content-wrapper, .leaflet-popup-content p').forEach(el => {
            el.style.fontSize = (size - 2) + 'px';
        });

        // Leaflet tooltips
        document.querySelectorAll('.leaflet-tooltip').forEach(el => {
            el.style.fontSize = (size - 2) + 'px';
        });
    }

    /**
     * Aumenta el tamaño de fuente
     */
    increaseFontSize() {
        const newSize = Math.min(this.currentSize + this.config.step, this.config.maxSize);
        if (newSize !== this.currentSize) {
            this.applyFontSize(newSize);
        }
    }

    /**
     * Disminuye el tamaño de fuente
     */
    decreaseFontSize() {
        const newSize = Math.max(this.currentSize - this.config.step, this.config.minSize);
        if (newSize !== this.currentSize) {
            this.applyFontSize(newSize);
        }
    }

    /**
     * Restaura el tamaño normal
     */
    resetFontSize() {
        this.applyFontSize(this.config.normalSize);
    }

    /**
     * Obtiene el tamaño actual
     */
    getCurrentSize() {
        return this.currentSize;
    }

    /**
     * Obtiene el porcentaje de zoom actual
     */
    getZoomPercentage() {
        const percentage = ((this.currentSize - this.config.minSize) / (this.config.maxSize - this.config.minSize)) * 100;
        return Math.round(percentage);
    }

    /**
     * Actualiza la UI de los controles (botones de accesibilidad)
     */
    updateControlsUI(size) {
        // Botón aumentar: desactivar si estamos en máximo
        const increaseBtn = document.getElementById('accessibility-increase');
        if (increaseBtn) {
            increaseBtn.disabled = size >= this.config.maxSize;
            increaseBtn.classList.toggle('disabled', size >= this.config.maxSize);
        }

        // Botón disminuir: desactivar si estamos en mínimo
        const decreaseBtn = document.getElementById('accessibility-decrease');
        if (decreaseBtn) {
            decreaseBtn.disabled = size <= this.config.minSize;
            decreaseBtn.classList.toggle('disabled', size <= this.config.minSize);
        }

        // Mostrar tamaño actual
        const sizeDisplay = document.getElementById('accessibility-size-display');
        if (sizeDisplay) {
            sizeDisplay.textContent = this.getZoomPercentage() + '%';
        }
    }
}

/**
 * Inicializar cuando el DOM esté listo
 */
let accessibilityManager = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        accessibilityManager = new AccessibilityManager();
    });
} else {
    accessibilityManager = new AccessibilityManager();
}

/**
 * Funciones globales para facilitar el uso en HTML
 */
function aumentarTexto() {
    if (accessibilityManager) accessibilityManager.increaseFontSize();
}

function disminuirTexto() {
    if (accessibilityManager) accessibilityManager.decreaseFontSize();
}

function restaurarTexto() {
    if (accessibilityManager) accessibilityManager.resetFontSize();
}

/**
 * Reinicializar accesibilidad cuando se cargan nuevos elementos dinámicamente
 * Útil para AJAX o carga dinámica de templates
 */
function reinitializeAccessibility() {
    if (accessibilityManager) {
        accessibilityManager.applyFontSize(accessibilityManager.getCurrentSize());
    }
}
