# ⚡ REFERENCIA RÁPIDA - ACCESIBILIDAD

## 📦 Archivos Creados/Modificados

| Archivo | Ubicación | Tipo | Estado |
|---------|-----------|------|--------|
| `accessibility.js` | `myapp/static/myapp/JAV/` | Nuevo | ✅ Creado |
| `accessibility.css` | `myapp/static/myapp/CSS/` | Nuevo | ✅ Creado |
| `base.html` | `myapp/templates/` | Modificado | ✅ Actualizado |
| `base.css` | `myapp/static/myapp/CSS/` | Modificado | ✅ Variables añadidas |

---

## 🎮 USO DEL USUARIO

```
Escritorio:  Navbar derecha → [−] | 100% | [+] | [⟲]
Móvil:       Menú ☰ → Accesibilidad → Botones
```

**Funciones:**
- **[−]** Disminuir (mín: 12px)
- **[+]** Aumentar (máx: 24px)
- **[⟲]** Restaurar (default: 16px)

---

## 💻 CÓDIGO PARA DESARROLLADORES

### Llamar desde HTML
```html
<button onclick="aumentarTexto()">+A</button>
<button onclick="disminuirTexto()">-A</button>
<button onclick="restaurarTexto()">Normal</button>
```

### Llamar desde JavaScript
```javascript
aumentarTexto();          // +2px
disminuirTexto();         // -2px
restaurarTexto();         // 16px (default)

// Obtener información
accessibilityManager.getCurrentSize();      // 18
accessibilityManager.getZoomPercentage();   // 50%

// Escuchar cambios
window.addEventListener('accessibilityChange', (e) => {
    console.log(e.detail.fontSize);
});

// Reinicializar después de AJAX
reinitializeAccessibility();
```

---

## 🔧 CONFIGURACIÓN

En `accessibility.js` línea ~16:

```javascript
this.config = {
    minSize: 12,              // Cambiar límite mín
    normalSize: 16,           // Cambiar default
    maxSize: 24,              // Cambiar límite máx
    step: 2,                  // Cambiar incremento
    storageKey: 'observatorio_font_size'
};
```

---

## 🎨 PERSONALIZAR ESTILOS

**Colores del menú** (`accessibility.css` línea ~180):
```css
.accessibility-menu {
    background-color: rgba(255, 255, 255, 0.1);  /* ← Cambiar */
}
```

**Tamaño de botones** (`accessibility.css` línea ~190):
```css
.accessibility-btn {
    min-width: 36px;      /* ← Cambiar */
    min-height: 36px;     /* ← Cambiar */
}
```

---

## 💾 ALMACENAMIENTO

**Local Storage:**
```javascript
localStorage.getItem('observatorio_font_size')    // Leer
localStorage.setItem('observatorio_font_size', 20)  // Guardar
localStorage.removeItem('observatorio_font_size')   // Limpiar
```

**Disponible en:** F12 → Storage → Local Storage

---

## 🐞 VERIFICAR FUNCIONAMIENTO

**En consola del navegador (F12):**
```javascript
// 1. Verificar que exista
console.log(accessibilityManager);  // Debe mostrar objeto

// 2. Probar función
aumentarTexto();

// 3. Ver tamaño actual
accessibilityManager.getCurrentSize();

// 4. Ver localStorage
localStorage.getItem('observatorio_font_size');

// 5. Forzar tamaño
accessibilityManager.applyFontSize(20);
```

---

## 📱 RESPONSIVE

- **Desktop (≥768px):** Botones en navbar
- **Móvil (<768px):** Menú en offcanvas

---

## 🌍 ELEMENTOS AFECTADOS

Automáticamente se ajustan:
- h1-h6 (títulos)
- p (párrafos)
- a (enlaces)
- button, .btn (botones)
- input, textarea, select (formularios)
- table, td, th (tablas)
- .card (cards)
- .navbar, .nav-link (navbar)
- .modal, .offcanvas (ventanas)
- footer (pie de página)
- #chat-widget (chat)
- .leaflet-popup-content (mapas)

---

## 🚀 INSTALAR/VERIFICAR

```bash
# 1. Verificar archivos existen
ls myapp/static/myapp/JAV/accessibility.js
ls myapp/static/myapp/CSS/accessibility.css

# 2. Recolectar estáticos (importante)
python manage.py collectstatic --noinput

# 3. Reiniciar servidor
python manage.py runserver

# 4. En navegador
# Ir a http://localhost:8000
# Buscar botones en navbar [−] [+] [⟲]
```

---

## 🔗 INTEGRACIÓN EN NUEVOS TEMPLATES

Todos heredan de `base.html` automáticamente:

```html
{% extends "base.html" %}

{% block content %}
<!-- Accesibilidad funciona aquí sin hacer nada -->
<h1>Título</h1>
<p>Párrafo</p>
{% endblock %}
```

---

## 🎯 EVENTO PERSONALIZADO

Cuando el tamaño cambia, se dispara:

```javascript
window.addEventListener('accessibilityChange', (event) => {
    // event.detail.fontSize → tamaño nuevo en px
    const newSize = event.detail.fontSize;
    console.log(`Nuevo: ${newSize}px`);
});
```

---

## ⌨️ ATAJOS DE TECLADO (Opcional)

Agregar en `accessibility.js`:

```javascript
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        if (e.key === '+' || e.key === '=') { e.preventDefault(); aumentarTexto(); }
        if (e.key === '-' || e.key === '_') { e.preventDefault(); disminuirTexto(); }
        if (e.key === '0') { e.preventDefault(); restaurarTexto(); }
    }
});
```

---

## 📊 VALORES GUARDADOS

**localStorage:** `observatorio_font_size`
- Tipo: String (número)
- Rango: 12-24
- Ejemplo: "18"

---

## 🔒 SEGURIDAD

- ✅ Sin APIs externas
- ✅ Solo localStorage local
- ✅ Sin info enviada a servidor
- ✅ XSS-safe

---

## 📞 SOPORTE RÁPIDO

| Problema | Solución |
|----------|----------|
| Botones no aparecen | Ejecutar `collectstatic` |
| No funciona | Limpiar caché (Ctrl+Shift+Del) |
| No persiste | Habilitar localStorage |
| Solo en desktop | Verificar offcanvas en móvil |
| Error en consola | Ver `accessibility.js` cargado |

---

## 📝 PRÓXIMAS MEJORAS

- [ ] Guardar en DB para usuarios autenticados
- [ ] Agregar modo alto contraste
- [ ] Agregar modo lectura/focus
- [ ] Sincronizar con sistema operativo

---

**Última revisión:** 2025-05-15 | **Estado:** ✅ Listo para producción
