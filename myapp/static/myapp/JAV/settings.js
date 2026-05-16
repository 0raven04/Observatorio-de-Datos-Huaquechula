/* ================================================================
   SETTINGS MANAGER — Observatorio Turístico de Huaquechula
   ================================================================
   Gestiona: Modal Settings, Accesibilidad, Traducción, Modo Oscuro
   Dependencias: accessibility.js (funciones de tamaño de texto)
   ================================================================ */

class SettingsManager {
    constructor() {
        this.modal         = null;
        this.isOpen        = false;
        this.currentTab    = 'accessibility';
        this.isAuthenticated = this.checkAuthentication();

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /* ── Inicialización ─────────────────────────────────────────── */
    init() {
        this.applyStoredTheme();   // Aplicar tema ANTES de pintar UI (sin parpadeo)
        this.createSettingsButton();
        this.createSettingsModal();
        this.setupEventListeners();
        this.setupGoogleTranslate();
        console.log('✓ Settings Manager inicializado');
    }

    /* ── Detectar autenticación ─────────────────────────────────── */
    checkAuthentication() {
        // Opción 1: atributo data-authenticated en body (puesto por Django)
        if (document.body.hasAttribute('data-authenticated')) {
            return document.body.getAttribute('data-authenticated') === 'true';
        }
        // Opción 2: elemento específico
        const authEl = document.querySelector('[data-user-authenticated]');
        if (authEl) return authEl.getAttribute('data-user-authenticated') === 'true';
        // Opción 3: sessionStorage
        const stored = sessionStorage.getItem('user_authenticated');
        if (stored !== null) return stored === 'true';
        return false;
    }

    /* ── Botón flotante ─────────────────────────────────────────── */
    createSettingsButton() {
        const btn = document.createElement('button');
        btn.id          = 'settings-button';
        btn.className   = 'settings-button';
        btn.title       = 'Configuración';
        btn.setAttribute('aria-label', 'Abrir configuración');
        btn.innerHTML   = '<i class="fas fa-cog"></i>';
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleModal();
        });
        document.body.appendChild(btn);
    }

    /* ── Modal HTML ─────────────────────────────────────────────── */
    createSettingsModal() {
        const container = document.createElement('div');
        container.id        = 'settings-modal';
        container.className = 'settings-modal';
        container.addEventListener('click', (e) => {
            if (e.target === container) this.closeModal();
        });

        const isDark       = document.documentElement.getAttribute('data-theme') === 'dark';
        const showTranslate = !this.isAuthenticated;

        container.innerHTML = `
            <div class="settings-modal-content">

                <!-- Header -->
                <div class="settings-modal-header">
                    <h2 class="settings-modal-title">
                        <i class="fas fa-cog"></i> Configuración
                    </h2>
                    <button class="settings-close-btn" aria-label="Cerrar" onclick="settingsManager.closeModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <!-- Tabs -->
                <div class="settings-tabs">
                    <button class="settings-tab-btn active" data-tab="accessibility">
                        <i class="fas fa-text-height"></i> Texto
                    </button>
                    <button class="settings-tab-btn" data-tab="theme">
                        <i class="fas fa-adjust"></i> Tema
                    </button>
                    ${showTranslate ? `
                    <button class="settings-tab-btn" data-tab="translation">
                        <i class="fas fa-globe"></i> Idioma
                    </button>` : ''}
                </div>

                <!-- Contenidos -->
                <div class="settings-tabs-container">

                    <!-- TAB: ACCESIBILIDAD -->
                    <div class="settings-tab-content active" id="tab-accessibility">
                        <div class="accessibility-section">
                            <div class="accessibility-item">
                                <span class="accessibility-label">
                                    <i class="fas fa-text-height"></i> Tamaño de Texto
                                </span>
                                <div class="accessibility-controls">
                                    <button class="settings-acc-btn" id="settings-decrease"
                                            onclick="settingsManager.disminuirTexto()">
                                        <i class="fas fa-minus"></i> A−
                                    </button>
                                    <button class="settings-acc-btn" id="settings-restore"
                                            onclick="settingsManager.restaurarTexto()">
                                        <i class="fas fa-redo"></i> Normal
                                    </button>
                                    <button class="settings-acc-btn" id="settings-increase"
                                            onclick="settingsManager.aumentarTexto()">
                                        <i class="fas fa-plus"></i> A+
                                    </button>
                                </div>
                            </div>

                            <div class="font-size-display">
                                <span>Tamaño Actual</span>
                                <span class="font-size-value" id="settings-font-size-display">100%</span>
                            </div>

                            <div class="settings-info-box">
                                <i class="fas fa-info-circle"></i>
                                <span>El cambio de tamaño se aplica a todo el sitio y se guarda automáticamente.</span>
                            </div>
                        </div>
                    </div>

                    <!-- TAB: TEMA (modo oscuro / claro) -->
                    <div class="settings-tab-content" id="tab-theme">
                        <div class="theme-section">
                            <div class="theme-item">
                                <span class="theme-label">
                                    <i class="fas fa-circle-half-stroke"></i> Modo de Visualización
                                </span>

                                <!-- Toggle switch -->
                                <div class="theme-toggle-row">
                                    <div class="theme-toggle-info">
                                        <div class="theme-toggle-icon" id="theme-icon">
                                            ${isDark ? '🌙' : '☀️'}
                                        </div>
                                        <div class="theme-toggle-text">
                                            <strong id="theme-label-text">
                                                ${isDark ? 'Modo Oscuro' : 'Modo Claro'}
                                            </strong>
                                            <small id="theme-label-sub">
                                                ${isDark ? 'Menos brillo, más confort nocturno' : 'Diseño original del sistema'}
                                            </small>
                                        </div>
                                    </div>
                                    <label class="theme-switch" title="Cambiar tema">
                                        <input type="checkbox" id="theme-toggle-checkbox"
                                               ${isDark ? 'checked' : ''}
                                               onchange="settingsManager.toggleTheme(this.checked)">
                                        <span class="theme-slider"></span>
                                    </label>
                                </div>

                                <!-- Preview cards -->
                                <div class="theme-preview">
                                    <div class="theme-preview-card light ${!isDark ? 'selected' : ''}"
                                         onclick="settingsManager.activarModoClaro()"
                                         title="Activar modo claro">
                                        ☀️ Modo Claro
                                    </div>
                                    <div class="theme-preview-card dark ${isDark ? 'selected' : ''}"
                                         onclick="settingsManager.activarModoOscuro()"
                                         title="Activar modo oscuro">
                                        🌙 Modo Oscuro
                                    </div>
                                </div>
                            </div>

                            <div class="settings-info-box">
                                <i class="fas fa-info-circle"></i>
                                <span>Tu preferencia de tema se guarda y se aplica automáticamente en cada visita.</span>
                            </div>
                        </div>
                    </div>

                    <!-- TAB: TRADUCCIÓN (solo páginas públicas) -->
                    ${showTranslate ? `
                    <div class="settings-tab-content" id="tab-translation">
                        <div class="translation-section">
                            <div class="translation-item">
                                <span class="translation-label">
                                    <i class="fas fa-language"></i> Idioma de la Página
                                </span>
                                <div class="google-translate-wrapper">
                                    <div id="google_translate_element_settings"></div>
                                </div>
                            </div>

                            <div class="translation-item">
                                <span class="translation-label">
                                    <i class="fas fa-star"></i> Idiomas Populares
                                </span>
                                <div class="language-selector">
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('es')">
                                        <span class="lang-flag">🇪🇸</span>
                                        <span class="lang-name">Español</span>
                                    </button>
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('en')">
                                        <span class="lang-flag">🇬🇧</span>
                                        <span class="lang-name">English</span>
                                    </button>
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('fr')">
                                        <span class="lang-flag">🇫🇷</span>
                                        <span class="lang-name">Français</span>
                                    </button>
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('de')">
                                        <span class="lang-flag">🇩🇪</span>
                                        <span class="lang-name">Deutsch</span>
                                    </button>
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('it')">
                                        <span class="lang-flag">🇮🇹</span>
                                        <span class="lang-name">Italiano</span>
                                    </button>
                                    <button class="lang-btn" onclick="settingsManager.changeLanguage('pt')">
                                        <span class="lang-flag">🇵🇹</span>
                                        <span class="lang-name">Português</span>
                                    </button>
                                </div>
                            </div>

                            <div class="translation-info">
                                <i class="fas fa-lightbulb"></i>
                                <span>Traducción proporcionada por Google Translate.</span>
                            </div>
                        </div>
                    </div>` : ''}

                </div><!-- /tabs-container -->

                <!-- Footer -->
                <div class="settings-modal-footer">
                    <span class="settings-footer-text">
                        <i class="fas fa-heart" style="color: var(--color-arena-oscuro);"></i>
                        Observatorio Turístico de Huaquechula
                    </span>
                </div>

            </div><!-- /modal-content -->
        `;

        document.body.appendChild(container);
        this.modal = container;
        this.setupTabListeners();
    }

    /* ── Listeners de tabs ──────────────────────────────────────── */
    setupTabListeners() {
        const buttons  = this.modal.querySelectorAll('.settings-tab-btn');
        const contents = this.modal.querySelectorAll('.settings-tab-content');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.getAttribute('data-tab'), buttons, contents);
            });
        });
    }

    switchTab(tabName, buttons, contents) {
        buttons.forEach(b  => b.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));
        const tabBtn     = this.modal.querySelector(`[data-tab="${tabName}"]`);
        const tabContent = this.modal.querySelector(`#tab-${tabName}`);
        if (tabBtn)     tabBtn.classList.add('active');
        if (tabContent) tabContent.classList.add('active');
        this.currentTab = tabName;
    }

    /* ── Event listeners globales ───────────────────────────────── */
    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) this.closeModal();
        });
        window.addEventListener('accessibilityChange', () => this.updateFontSizeDisplay());
        window.addEventListener('storage', () => this.updateFontSizeDisplay());
    }

    /* ── Google Translate ────────────────────────────────────────── */
    setupGoogleTranslate() {
        if (this.isAuthenticated) return;
        if (!window.googleTranslateScriptLoaded) {
            const s   = document.createElement('script');
            s.type    = 'text/javascript';
            s.src     = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
            document.head.appendChild(s);
            window.googleTranslateScriptLoaded = true;
        }
        window.googleTranslateElementInit = () => {
            if (typeof google !== 'undefined' && google.translate) {
                new google.translate.TranslateElement({
                    pageLanguage: 'es',
                    includedLanguages: 'es,en,fr,de,it,pt',
                    layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
                }, 'google_translate_element_settings');
            }
        };
    }

    changeLanguage(langCode) {
        // Marcar botón activo visualmente
        const langBtns = this.modal?.querySelectorAll('.lang-btn');
        langBtns?.forEach(btn => {
            const onclick = btn.getAttribute('onclick') || '';
            btn.classList.toggle('active', onclick.includes(`'${langCode}'`));
        });

        localStorage.setItem('observatorio_language', langCode);

        if (langCode === 'es') {
            this._restoreOriginalLanguage();
            return;
        }

        // Método más confiable: cookie googtrans + recarga
        // Google Translate SIEMPRE lee esta cookie al cargar la página
        const cookieValue = `/auto/${langCode}`;
        document.cookie = `googtrans=${cookieValue}; path=/`;
        document.cookie = `googtrans=${cookieValue}; path=/; domain=${window.location.hostname}`;

        // Intentar aplicar sin recargar primero (si el widget está listo)
        const combo = document.querySelector('select.goog-te-combo');
        if (combo) {
            combo.value = langCode;
            combo.dispatchEvent(new Event('change', { bubbles: true }));
            // Verificar si funcionó; si no, recargar
            setTimeout(() => {
                if (!document.body.classList.contains('translated-ltr') &&
                    !document.body.classList.contains('translated-rtl')) {
                    window.location.reload();
                }
            }, 1500);
        } else {
            // Widget no disponible → recargar con cookie ya establecida
            window.location.reload();
        }
    }

    _restoreOriginalLanguage() {
        // Limpiar cookies de traducción (todas las variantes)
        const exp = 'expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/';
        const host = window.location.hostname;
        document.cookie = `googtrans=; ${exp}`;
        document.cookie = `googtrans=; ${exp}; domain=${host}`;
        document.cookie = `googtrans=; ${exp}; domain=.${host}`;

        // Método 1: clic en el botón de restaurar del banner de Google
        try {
            const iframe = document.querySelector('.goog-te-banner-frame');
            if (iframe?.contentDocument) {
                const restoreBtn = iframe.contentDocument.querySelector('[id$=".restore"]') ||
                                   iframe.contentDocument.querySelector('.goog-close-link');
                if (restoreBtn) {
                    restoreBtn.click();
                    return; // No recargar si el banner lo maneja
                }
            }
        } catch (e) { /* cross-origin: ignorar */ }

        // Método 2: recargar si la página estaba traducida
        if (document.body.classList.contains('translated-ltr') ||
            document.body.classList.contains('translated-rtl') ||
            document.querySelector('.goog-te-banner-frame')) {
            window.location.reload();
        }
    }

    /* ══════════════════════════════════════════════════════════════
       MODO OSCURO / CLARO
       ══════════════════════════════════════════════════════════════ */

    /**
     * Aplica el tema guardado en localStorage sin parpadeo.
     * Llamar ANTES de que el DOM se pinte (al inicio de init()).
     */
    applyStoredTheme() {
        const saved = localStorage.getItem('observatorio_theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
    }

    /** Activa el modo oscuro */
    activarModoOscuro() {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('observatorio_theme', 'dark');
        this._syncThemeUI(true);
    }

    /** Activa el modo claro */
    activarModoClaro() {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('observatorio_theme', 'light');
        this._syncThemeUI(false);
    }

    /** Toggle desde el switch */
    toggleTheme(isDark) {
        if (isDark) {
            this.activarModoOscuro();
        } else {
            this.activarModoClaro();
        }
    }

    /** Sincroniza todos los elementos de la UI del tema */
    _syncThemeUI(isDark) {
        // Checkbox
        const checkbox = this.modal?.querySelector('#theme-toggle-checkbox');
        if (checkbox) checkbox.checked = isDark;

        // Icono y textos
        const icon    = this.modal?.querySelector('#theme-icon');
        const label   = this.modal?.querySelector('#theme-label-text');
        const subLabel = this.modal?.querySelector('#theme-label-sub');
        if (icon)     icon.textContent  = isDark ? '🌙' : '☀️';
        if (label)    label.textContent = isDark ? 'Modo Oscuro' : 'Modo Claro';
        if (subLabel) subLabel.textContent = isDark
            ? 'Menos brillo, más confort nocturno'
            : 'Diseño original del sistema';

        // Cards de preview
        const lightCard = this.modal?.querySelector('.theme-preview-card.light');
        const darkCard  = this.modal?.querySelector('.theme-preview-card.dark');
        if (lightCard) lightCard.classList.toggle('selected', !isDark);
        if (darkCard)  darkCard.classList.toggle('selected', isDark);
    }

    /* ══════════════════════════════════════════════════════════════
       ACCESIBILIDAD
       ══════════════════════════════════════════════════════════════ */

    aumentarTexto() {
        if (window.accessibilityManager) {
            window.accessibilityManager.increaseFontSize();
        } else if (typeof aumentarTexto === 'function') {
            aumentarTexto();
        }
        this.updateFontSizeDisplay();
    }

    disminuirTexto() {
        if (window.accessibilityManager) {
            window.accessibilityManager.decreaseFontSize();
        } else if (typeof disminuirTexto === 'function') {
            disminuirTexto();
        }
        this.updateFontSizeDisplay();
    }

    restaurarTexto() {
        if (window.accessibilityManager) {
            window.accessibilityManager.resetFontSize();
        } else if (typeof restaurarTexto === 'function') {
            restaurarTexto();
        }
        this.updateFontSizeDisplay();
    }

    updateFontSizeDisplay() {
        let pct = '100%';
        if (window.accessibilityManager) {
            pct = window.accessibilityManager.getZoomPercentage() + '%';
        } else {
            const stored = localStorage.getItem('observatorio_font_size');
            if (stored) {
                const s = parseInt(stored);
                pct = ((s - 16) / 16 * 100 + 100).toFixed(0) + '%';
            }
        }
        const display = this.modal?.querySelector('#settings-font-size-display');
        if (display) display.textContent = pct;
    }

    /* ── Modal open / close ─────────────────────────────────────── */
    toggleModal() {
        this.isOpen ? this.closeModal() : this.openModal();
    }

    openModal() {
        if (!this.modal) return;
        this.modal.classList.add('active');
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
        this.updateFontSizeDisplay();
        this._syncThemeUI(
            document.documentElement.getAttribute('data-theme') === 'dark'
        );
    }

    closeModal() {
        if (!this.modal) return;
        this.modal.classList.remove('active');
        this.isOpen = false;
        document.body.style.overflow = '';
    }

    reinitialize() { this.updateFontSizeDisplay(); }

    getStatus() {
        return {
            isOpen:       this.isOpen,
            isAuth:       this.isAuthenticated,
            currentTab:   this.currentTab,
            theme:        localStorage.getItem('observatorio_theme') || 'light',
            fontSize:     localStorage.getItem('observatorio_font_size') || '16',
            language:     localStorage.getItem('observatorio_language') || 'es',
        };
    }
}

/* ================================================================
   INICIALIZACIÓN GLOBAL
   ================================================================ */

/* Aplicar tema INMEDIATAMENTE (antes del DOMContentLoaded) para
   evitar parpadeo blanco → oscuro al cargar */
(function () {
    const t = localStorage.getItem('observatorio_theme') || 'light';
    document.documentElement.setAttribute('data-theme', t);
})();

let settingsManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        settingsManager = new SettingsManager();
    });
} else {
    settingsManager = new SettingsManager();
}

/* ================================================================
   FUNCIONES GLOBALES DE ACCESO RÁPIDO
   ================================================================ */

function openSettings()    { settingsManager?.openModal();   }
function closeSettings()   { settingsManager?.closeModal();  }
function toggleSettings()  { settingsManager?.toggleModal(); }

function activarModoOscuro() { settingsManager?.activarModoOscuro(); }
function activarModoClaro()  { settingsManager?.activarModoClaro();  }
function toggleTheme(isDark) { settingsManager?.toggleTheme(isDark); }

console.log('✓ Settings Manager cargado | Uso: settingsManager.getStatus()');
