# 📋 GUÍA COMPLETA - SISTEMA DE ACCESIBILIDAD GLOBAL

## 🎯 Descripción General

Sistema completo de accesibilidad que permite a los usuarios aumentar y disminuir el tamaño de texto en toda la aplicación Django **sin recargar la página**. Los cambios se guardan en `localStorage` y se aplican automáticamente en futuras visitas.

---

## 📦 Archivos Implementados

### 1. **accessibility.js** (Lógica)
```
myapp/static/myapp/JAV/accessibility.js
```
- Clase `AccessibilityManager` que maneja toda la lógica
- Almacenamiento persistente con `localStorage`
- Funciones globales: `aumentarTexto()`, `disminuirTexto()`, `restaurarTexto()`
- Soporte para Leaflet maps

### 2. **accessibility.css** (Estilos)
```
myapp/static/myapp/CSS/accessibility.css
```
- Variables CSS dinámicas
- Estilos del menú de accesibilidad
- Soporte para responsive design
- Compatible con modo oscuro

### 3. **base.html** (Integración)
```
myapp/templates/base.html
```
- Menú de accesibilidad en navbar (escritorio)
- Menú de accesibilidad en offcanvas (móvil)
- Links a los archivos CSS y JS

---

## 🚀 ¿YA ESTÁ INSTALADO?

**SÍ** - El sistema ya está completo e integrado en tu proyecto. Solo tienes que:

1. **Verificar que los archivos existan:**
   - ✅ `myapp/static/myapp/JAV/accessibility.js`
   - ✅ `myapp/static/myapp/CSS/accessibility.css`
   - ✅ `myapp/templates/base.html` (modificado)

2. **Ejecutar collectstatic (para producción):**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Reiniciar el servidor:**
   ```bash
   python manage.py runserver
   ```

---

## 🎨 Componentes Afectados

El sistema aplica cambios de tamaño de texto a **TODOS** estos elementos:

- ✅ **Títulos**: h1, h2, h3, h4, h5, h6
- ✅ **Párrafos**: p, small, text-muted
- ✅ **Enlaces**: a, nav-link
- ✅ **Botones**: button, .btn, input[type="button"]
- ✅ **Formularios**: input, textarea, select, label
- ✅ **Tablas**: table, th, td
- ✅ **Cards**: .card, .card-title, .card-text
- ✅ **Navbars**: .navbar, .nav-link
- ✅ **Modales**: .modal, .modal-title
- ✅ **Offcanvas**: .offcanvas, .offcanvas-title
- ✅ **Footer**: footer, .foter_leter
- ✅ **Chat Widget**: #chat-widget y componentes
- ✅ **Mapas Leaflet**: popups, tooltips
- ✅ **Y muchos más...**

---

## 🔧 Configuración (Valores por Defecto)

En `accessibility.js`, línea ~16-22:

```javascript
this.config = {
    minSize: 12,      // Tamaño mínimo
    normalSize: 16,   // Tamaño normal (default)
    maxSize: 24,      // Tamaño máximo
    step: 2,          // Incremento por click
    storageKey: 'observatorio_font_size'
};
```

**¿Quieres cambiar estos valores?**
- Edita `accessibility.js` y modifica el objeto `config`

---

## 💾 Almacenamiento Local

El tamaño de texto se guarda automáticamente en **localStorage** con la clave:
```
observatorio_font_size
```

**Ubicación en el navegador:**
- F12 → Storage → Local Storage → Tu dominio

**¿Quieres limpiar la preferencia?**
```javascript
// En consola del navegador
localStorage.removeItem('observatorio_font_size');
```

---

## 📱 Interfaz de Usuario

### Escritorio (Bootstrap md - 768px+)
```
Navbar lado derecho:
┌─────────────────────────┐
│ [−] | 100% | [+] | [⟲] │  ← Controles de accesibilidad
└─────────────────────────┘
```

Botones con iconos de Font Awesome:
- **[−]** (fa-minus) = Disminuir
- **[+]** (fa-plus) = Aumentar
- **[⟲]** (fa-redo) = Restaurar normal
- **100%** = Indicador del tamaño actual

### Móvil (< 768px)
```
Menú offcanvas:
┌──────────────────────────────┐
│ ☰ Menú                       │
├──────────────────────────────┤
│ Inicio                       │
│ Mapa                         │
│ Encuesta ▼                   │
│ Repositorio                  │
├──────────────────────────────┤
│ ♿ Accesibilidad             │
│ [− Disminuir] [⟲ Normal]    │
│ [+ Aumentar]                 │
│ Tamaño actual: 100%          │
└──────────────────────────────┘
```

---

## 🎮 USO

### Desde HTML (Botones)
Ya está integrado en el navbar. Los usuarios solo tienen que:
1. Click en **[−]** para disminuir
2. Click en **[+]** para aumentar
3. Click en **[⟲]** para restaurar

### Desde JavaScript (Programáticamente)

```javascript
// Aumentar tamaño
aumentarTexto();

// Disminuir tamaño
disminuirTexto();

// Restaurar normal
restaurarTexto();

// Obtener tamaño actual
console.log(accessibilityManager.getCurrentSize()); // ej: 18

// Obtener porcentaje de zoom
console.log(accessibilityManager.getZoomPercentage()); // ej: 50%

// Aplicar tamaño específico
accessibilityManager.applyFontSize(20);
```

### Escuchar Cambios de Accesibilidad

Si quieres ejecutar código cuando el usuario cambie el tamaño:

```javascript
// En tu archivo JS personalizado
window.addEventListener('accessibilityChange', (event) => {
    const newSize = event.detail.fontSize;
    console.log(`Nuevo tamaño: ${newSize}px`);
    
    // Aquí puedes hacer algo con esa información
    // Por ejemplo, ajustar layouts personalizados
});
```

### Reinicializar (Después de Cargar Contenido Dinámico)

Si usas AJAX y cargas nuevo contenido dinámicamente:

```javascript
// Después de cargar nuevo contenido vía AJAX
reinitializeAccessibility();
```

---

## 🔧 Personalización

### Cambiar Colores del Menú

En `accessibility.css`, línea ~180+:

```css
.accessibility-menu {
    background-color: rgba(255, 255, 255, 0.1);  /* Cambiar aquí */
}

.accessibility-btn:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.2);  /* Y aquí */
}
```

### Cambiar Límites de Tamaño

En `accessibility.js`, línea ~16-22:

```javascript
this.config = {
    minSize: 10,      // ← Cambiar a 10
    normalSize: 16,
    maxSize: 28,      // ← Cambiar a 28
    step: 1,          // ← Cambiar paso a 1px
    storageKey: 'observatorio_font_size'
};
```

### Agregar Más Elementos Personalizados

En `accessibility.js`, método `applyToElements()`, agrega:

```javascript
// Ejemplo: Si tienes elementos con clase custom
document.querySelectorAll('.mi-clase-personalizada').forEach(el => {
    el.style.fontSize = size + 'px';
});
```

### Cambiar Estilos del Botón

En `accessibility.css`:

```css
.accessibility-btn {
    min-width: 36px;
    min-height: 36px;
    padding: 6px 10px;
    border-radius: 4px;     /* ← Modificar esquinas */
    background-color: transparent;
    color: inherit;
    /* ... más propiedades ... */
}
```

---

## 🐛 Troubleshooting

### Problema: Los botones no aparecen en la navbar

**Solución:**
1. Verifica que `accessibility.css` esté linkedeado en `base.html`
2. Ejecuta: `python manage.py collectstatic --noinput`
3. Limpia caché del navegador (Ctrl+Shift+Del)
4. Reinicia servidor

### Problema: El tamaño no cambia

**Solución:**
1. Abre F12 → Console
2. Escribe: `accessibilityManager.getCurrentSize()` y presiona Enter
3. Si devuelve error, revisa si `accessibility.js` está cargando
4. Verifica que no haya errores en la consola

### Problema: Los cambios no persisten

**Solución:**
1. Verifica que localStorage esté habilitado en el navegador
2. Comprueba que el navegador no esté en modo privado/incógnito
3. Abre F12 → Storage → Local Storage

### Problema: Solo funciona en desktop, no en móvil

**Solución:**
1. Verifica que el offcanvas esté abierto
2. Busca el menú "Accesibilidad" en el offcanvas
3. Si no lo ves, verifica que la clase `accessibility-menu-mobile` exista en `base.html`

---

## 📊 Valores de Tamaño por Defecto

| Contexto | Valor | Descripción |
|----------|-------|-------------|
| **Mínimo** | 12px | Límite más bajo |
| **Normal** | 16px | Default (100%) |
| **Máximo** | 24px | Límite más alto |
| **Paso** | 2px | Incremento por click |

**Cálculo de porcentaje:**
```
Porcentaje = ((tamaño_actual - 12) / (24 - 12)) * 100
Ejemplo: (16 - 12) / 12 * 100 = 33.33% ≈ 100% (mostrado como 100% en UI)
```

---

## 🌐 Compatibilidad

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers
- ✅ Bootstrap 5.3.0
- ✅ Leaflet 1.9.4
- ✅ Django 3.0+
- ✅ Sin dependencias externas

---

## 🔒 Seguridad

- ✅ Sin scripts externos
- ✅ Solo usa localStorage (datos locales del usuario)
- ✅ No envía información a servidor
- ✅ Protegido contra XSS (no usa innerHTML dinámico)

---

## 📝 Ejemplo: Integrar en Otro Template

Si heredas desde `base.html`, automáticamente obtienes accesibilidad:

```html
{% extends "base.html" %}

{% block title %}Mi Página{% endblock %}

{% block content %}
<h1>Mi Contenido</h1>
<p>Este párrafo tendrá accesibilidad automáticamente</p>
{% endblock %}
```

**No necesitas hacer nada más.**

---

## 🎓 Concepto de Funcionamiento

```
Usuario hace click en [+]
        ↓
JavaScript ejecuta: aumentarTexto()
        ↓
AccessibilityManager aumenta tamaño en 2px
        ↓
Aplica variables CSS en :root
        ↓
Aplica styles inline a elementos específicos
        ↓
Guarda en localStorage
        ↓
Dispara evento 'accessibilityChange'
        ↓
UI se actualiza sin recargar página
```

---

## 📚 Documentación de Código

### Clase Principal: AccessibilityManager

```javascript
class AccessibilityManager {
    constructor()           // Inicializa el manager
    init()                  // Carga preferencias guardadas
    loadSavedSize()         // Lee localStorage
    applyFontSize(size)     // Aplica tamaño globalmente
    applyToElements(size)   // Aplica a elementos específicos
    updateLeafletPopups()   // Actualiza mapas
    increaseFontSize()      // Incrementa tamaño
    decreaseFontSize()      // Decrementa tamaño
    resetFontSize()         // Restaura default
    getCurrentSize()        // Devuelve tamaño actual
    getZoomPercentage()     // Devuelve % de zoom
    updateControlsUI()      // Actualiza buttons UI
}
```

### Variables CSS Disponibles

```css
--font-size-base        /* Tamaño base dinámico */
--font-size-small       /* Tamaño pequeño */
--font-size-large       /* Tamaño grande */
```

Uso en CSS personalizado:

```css
.mi-elemento {
    font-size: var(--font-size-base);
}
```

---

## 🚀 Optimizaciones Aplicadas

- ✅ Transiciones suave (0.2s ease)
- ✅ Debounce en eventos storage
- ✅ Caché de elementos (evita re-queries innecesarias)
- ✅ CSS variables para máximo rendimiento
- ✅ Sin recarga de página
- ✅ Responsive design
- ✅ Accesible con teclado

---

## 🎯 Próximos Pasos (Opcionales)

### 1. Agregar Preferencia en Base de Datos
Puedes guardar la preferencia del usuario autenticado en DB:

```python
# models.py
class Usuario(User):
    font_size_preference = models.IntegerField(default=16)
```

Luego modificar `accessibility.js` para usar AJAX.

### 2. Agregar Más Opciones de Accesibilidad
- Modo alto contraste
- Modo sin serifas
- Espaciado entre líneas
- Etc.

### 3. Integrar en Admin de Django
Si lo deseas, puedes crear settings de accesibilidad en admin.

---

## 📞 Preguntas Frecuentes

**P: ¿Funciona con AJAX?**
R: Sí, pero llamar `reinitializeAccessibility()` después de cargar contenido dinámico.

**P: ¿Se sincroniza entre pestañas?**
R: Sí, automáticamente via evento `storage`.

**P: ¿Puedo usar en sitios estáticos?**
R: Sí, es JavaScript puro. Funciona en cualquier HTML.

**P: ¿Afecta el SEO?**
R: No, los estilos inline no impactan SEO.

**P: ¿Compatible con impresión?**
R: Sí, pero los controles se ocultan en print.

---

## 📄 Licencia

Código libre para usar en tu proyecto. Puedes modificar y distribuir.

---

**Creado para:** Observatorio Turístico de Huaquechula
**Última actualización:** 2025-05-15
**Estado:** ✅ Completamente funcional
