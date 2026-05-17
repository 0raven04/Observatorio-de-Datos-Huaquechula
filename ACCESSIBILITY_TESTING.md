# 🧪 TESTING Y VALIDACIÓN - ACCESIBILIDAD

## ✅ Checklist de Verificación

### 1️⃣ Archivos Existentes

- [ ] `myapp/static/myapp/JAV/accessibility.js` existe
- [ ] `myapp/static/myapp/CSS/accessibility.css` existe
- [ ] `myapp/templates/base.html` contiene cambios
- [ ] `myapp/static/myapp/CSS/base.css` tiene variables CSS

```bash
# Verificar desde terminal
ls -la myapp/static/myapp/JAV/accessibility.js
ls -la myapp/static/myapp/CSS/accessibility.css
```

### 2️⃣ Verificación Visual

#### Desktop (≥768px)
1. Abre http://localhost:8000
2. En navbar derecha debe haber: `[−] | 100% | [+] | [⟲]`
3. Botones con iconos de Font Awesome
4. Fondo semi-transparente

#### Móvil (<768px)
1. Abre http://localhost:8000 en móvil o redimensiona
2. Abre menú ☰
3. Busca sección "♿ Accesibilidad"
4. Debe haber botones con etiquetas

### 3️⃣ Pruebas Funcionales

**En consola del navegador (F12):**

```javascript
// Test 1: Objeto existe
console.assert(accessibilityManager !== undefined, 'AccessibilityManager no existe');

// Test 2: Tamaño actual
const currentSize = accessibilityManager.getCurrentSize();
console.assert(currentSize >= 12 && currentSize <= 24, `Tamaño inválido: ${currentSize}`);

// Test 3: Aumentar
const before = accessibilityManager.getCurrentSize();
aumentarTexto();
const after = accessibilityManager.getCurrentSize();
console.assert(after > before, 'aumentarTexto() no funcionó');

// Test 4: Disminuir
const before2 = accessibilityManager.getCurrentSize();
disminuirTexto();
const after2 = accessibilityManager.getCurrentSize();
console.assert(after2 < before2, 'disminuirTexto() no funcionó');

// Test 5: Restaurar
restaurarTexto();
const restored = accessibilityManager.getCurrentSize();
console.assert(restored === 16, `restaurarTexto() no funcionó: ${restored}`);

// Test 6: localStorage
const saved = localStorage.getItem('observatorio_font_size');
console.assert(saved !== null, 'localStorage no está guardando');
console.log(`Valor guardado: ${saved}`);

// Test 7: Evento
let eventFired = false;
window.addEventListener('accessibilityChange', () => { eventFired = true; });
aumentarTexto();
console.assert(eventFired, 'Evento accessibilityChange no se dispara');

console.log('✅ Todos los tests pasaron');
```

**Copiar y pegar en consola F12 → Console**

### 4️⃣ Pruebas de Elementos

```javascript
// Test que los elementos cambien tamaño
const originalSize = window.getComputedStyle(document.body).fontSize;
aumentarTexto();
const newSize = window.getComputedStyle(document.body).fontSize;

if (originalSize !== newSize) {
    console.log('✅ Tamaño de body cambió');
} else {
    console.warn('⚠️ Tamaño de body NO cambió');
}

// Test que h1 cambió
const h1 = document.querySelector('h1');
if (h1) {
    console.log(`h1 original: ${h1.style.fontSize || 'no definido'}`);
    aumentarTexto();
    console.log(`h1 después: ${h1.style.fontSize}`);
}

// Test que botones cambien
const buttons = document.querySelectorAll('button');
console.log(`Botones encontrados: ${buttons.length}`);
buttons.forEach((btn, i) => {
    if (btn.style.fontSize) {
        console.log(`Botón ${i}: ${btn.style.fontSize}`);
    }
});
```

### 5️⃣ Pruebas de Persistencia

1. Abre app
2. Aumenta tamaño a máximo
3. Cierra navegador
4. Reabre app
5. Debe estar en tamaño máximo

```javascript
// Script para verificar
localStorage.setItem('test_persistencia', new Date());
console.log('Salvado. Abre nueva pestaña y ejecuta:');
console.log("localStorage.getItem('test_persistencia')");
```

### 6️⃣ Pruebas de Responsiveness

**Desktop:**
1. Abre DevTools (F12)
2. Redimensiona a 1200px
3. Botones deben estar visibles en navbar

**Tablet:**
1. Redimensiona a 1024px
2. Botones deben estar visibles

**Móvil:**
1. Redimensiona a 375px
2. Botones deben estar OCULTOS en navbar
3. Deben aparecer en menú offcanvas

### 7️⃣ Pruebas de Navegadores

| Navegador | Desktop | Móvil | localStorage | CSS Variables |
|-----------|---------|-------|--------------|----------------|
| Chrome 90+ | ✅ | ✅ | ✅ | ✅ |
| Firefox 88+ | ✅ | ✅ | ✅ | ✅ |
| Safari 14+ | ✅ | ✅ | ✅ | ✅ |
| Edge 90+ | ✅ | ✅ | ✅ | ✅ |

### 8️⃣ Pruebas de Accesibilidad (WCAG)

```javascript
// Verificar que no haya errores de consola
window.addEventListener('error', (e) => {
    if (e.message.includes('accessibility')) {
        console.error('Error en accesibilidad:', e);
    }
});

// Verificar que los botones sean accesibles
document.querySelectorAll('.accessibility-btn').forEach(btn => {
    const hasTitle = btn.hasAttribute('title');
    const hasAriaLabel = btn.hasAttribute('aria-label');
    if (!hasTitle && !hasAriaLabel) {
        console.warn('Botón sin title o aria-label:', btn);
    }
});
```

### 9️⃣ Pruebas de Rendimiento

```javascript
// Medir tiempo de aplicación
const start = performance.now();
aumentarTexto();
const end = performance.now();
console.log(`Tiempo de cambio: ${(end - start).toFixed(2)}ms`);
// Debe ser < 100ms

// Medir memoria
if (performance.memory) {
    console.log(`Memoria usada: ${(performance.memory.usedJSHeapSize / 1048576).toFixed(2)}MB`);
}
```

### 🔟 Pruebas de Mapas (Leaflet)

Si tienes mapas, verifica en `/mapa`:

```javascript
// En página del mapa, ejecuta:
window.addEventListener('accessibilityChange', (e) => {
    console.log('Cambio de accesibilidad detectado en mapa');
    // El mapa debería reajustarse
});

aumentarTexto();
// Verifica que los popups de Leaflet también aumenten
```

---

## 🐛 Troubleshooting

### Síntoma: "accessibility.js not found"

```
❌ Error: Failed to load script
```

**Soluciones:**
1. Verificar ruta del archivo
2. Ejecutar `python manage.py collectstatic --noinput`
3. Limpiar caché: Ctrl+Shift+Del

### Síntoma: "accessibilityManager is undefined"

```
❌ ReferenceError: accessibilityManager is not defined
```

**Soluciones:**
1. Verificar que `accessibility.js` esté en `<head>` o `<body>`
2. Verificar que el atributo `defer` esté en el script
3. Esperar a que el DOM esté listo:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    console.log(accessibilityManager);
});
```

### Síntoma: "Botones no cambian el tamaño"

**Soluciones:**
1. Verificar que `accessibility.css` esté linkedeado
2. Revisar en Inspector que la variable CSS esté aplicada
3. F12 → Inspector → `<body>` → buscar `style="font-size"`

### Síntoma: "localStorage no guarda"

**Soluciones:**
1. Verificar que no esté en modo privado/incógnito
2. Verificar que localStorage esté habilitado en navegador
3. Probar: `localStorage.setItem('test', 'valor')` en consola

### Síntoma: "En móvil no aparece el menú de accesibilidad"

**Soluciones:**
1. Verificar que el offcanvas esté funcionando
2. Buscar manualmente el botón ☰
3. Verificar que la clase `accessibility-menu-mobile` exista

---

## 📋 Script de Testing Automatizado

Crea archivo `test_accessibility.js`:

```javascript
/**
 * Script de testing para accesibilidad
 * Ejecutar en consola: eval(fetch('test_accessibility.js').then(r => r.text()))
 */

const tests = {
    managerExists: () => typeof accessibilityManager !== 'undefined',
    functionsExist: () => {
        return typeof window.aumentarTexto === 'function' &&
               typeof window.disminuirTexto === 'function' &&
               typeof window.restaurarTexto === 'function';
    },
    storageWorks: () => {
        localStorage.setItem('test', 'value');
        const result = localStorage.getItem('test') === 'value';
        localStorage.removeItem('test');
        return result;
    },
    buttonsPresent: () => document.querySelectorAll('.accessibility-btn').length > 0,
    cssVariablesSet: () => {
        const value = getComputedStyle(document.documentElement)
            .getPropertyValue('--font-size-base');
        return value && value.includes('px');
    },
    eventWorks: () => {
        let fired = false;
        window.addEventListener('accessibilityChange', () => { fired = true; }, { once: true });
        aumentarTexto();
        return fired;
    }
};

const results = {};
for (const [test, fn] of Object.entries(tests)) {
    try {
        results[test] = fn() ? '✅' : '❌';
    } catch (e) {
        results[test] = `❌ ${e.message}`;
    }
}

console.table(results);
const passed = Object.values(results).filter(r => r === '✅').length;
console.log(`\n${passed}/${Object.keys(results).length} tests pasaron`);
```

---

## 📊 Reporte de Verificación

**Copiar y pegar cuando todo esté listo:**

```
## ✅ VERIFICACIÓN DE ACCESIBILIDAD COMPLETADA

- Archivos creados: ✅
- Funcionalidad básica: ✅
- Persistencia: ✅
- Responsiveness: ✅
- Navegadores: ✅
- Mapas/Popups: ✅

Listos para PRODUCCIÓN.
```

---

## 🎓 Pruebas Manuales Sugeridas

1. **Primera visita:**
   - Aumentar tamaño a máximo
   - Verificar todos los elementos cambien
   - Notar que se ve más grande

2. **Recarga de página:**
   - F5 o Ctrl+R
   - Debe mantener el tamaño máximo

3. **Nueva pestaña:**
   - Ctrl+T
   - Abrir la app
   - Debe estar en tamaño normal (no heredar)
   - Aumentar en esta pestaña
   - Original debe estar en máximo (sincronización)

4. **Diferentes páginas:**
   - Ir a /mapa
   - Ir a /repositorio
   - Ir a /formulario
   - Todos deben mantener el tamaño

5. **Formularios:**
   - Aumentar texto
   - Inputs deben verse más grandes
   - Placeholders deben ser legibles

6. **Tablas:**
   - Si existen, aumentar
   - Contenido debe ser legible

7. **Modales:**
   - Abrir modal (si existe)
   - Aumentar texto
   - Modal debe ajustarse

8. **Chat widget:**
   - Abrir chat
   - Aumentar texto
   - Chat debe cambiar

---

**Cuando todos los tests pasen, está listo para producción.**
