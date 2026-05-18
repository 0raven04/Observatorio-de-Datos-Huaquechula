# 📋 INSTRUCCIONES PARA ACTUALIZAR README.md

## Agregar esta sección al README.md del proyecto

```markdown
---

## ♿ ACCESIBILIDAD - Cambio de Tamaño de Texto

### ✨ Característica Nueva

El sistema incluye un módulo completo de accesibilidad que permite a los usuarios aumentar y disminuir el tamaño de texto **dinámicamente en toda la aplicación** sin necesidad de recargar la página.

### 🎮 Cómo Usar

#### Para Usuarios Finales

1. **Desktop:** Busca los botones en la esquina superior derecha del navbar
   - **[−]** Disminuir tamaño
   - **[100%]** Indicador de tamaño actual
   - **[+]** Aumentar tamaño
   - **[⟲]** Restaurar tamaño normal

2. **Móvil:** Abre el menú (☰) y busca la sección "Accesibilidad"

3. **Teclado (Opcional):**
   - `Ctrl + +` / `Cmd + +` = Aumentar
   - `Ctrl + -` / `Cmd + -` = Disminuir
   - `Ctrl + 0` / `Cmd + 0` = Restaurar

### 🔧 Configuración Técnica

**Rango de tamaños:**
- Mínimo: 12px
- Normal (default): 16px
- Máximo: 24px
- Incremento por click: 2px

**Almacenamiento:** Las preferencias se guardan automáticamente en `localStorage` y se restauran en futuras visitas.

### 📁 Archivos Incluidos

```
myapp/static/myapp/
├── JAV/
│   └── accessibility.js          ← Lógica principal
└── CSS/
    └── accessibility.css         ← Estilos del menú

myapp/templates/
└── base.html                     ← Menú integrado

ACCESSIBILITY_GUIDE.md            ← Documentación completa
ACCESSIBILITY_EXAMPLES.md         ← Ejemplos y personalizaciones
ACCESSIBILITY_QUICK_REFERENCE.md  ← Referencia rápida
ACCESSIBILITY_TESTING.md          ← Testing y troubleshooting
```

### 🎯 Elementos Afectados

El cambio de tamaño se aplica automáticamente a:
- Títulos (h1-h6)
- Párrafos y texto
- Botones
- Formularios (inputs, textareas)
- Tablas
- Cards y componentes Bootstrap
- Navbar y menús
- Modales y ventanas
- Footer
- Chat widget
- Mapas interactivos (Leaflet popups)
- Y más...

### 🚀 Instalación

**Ya está instalado.** Solo necesitas:

```bash
# 1. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 2. Reiniciar servidor
python manage.py runserver
```

Luego abre http://localhost:8000 y busca los botones en navbar.

### 💻 Para Desarrolladores

**Llamar desde HTML:**
```html
<button onclick="aumentarTexto()">Aumentar</button>
<button onclick="disminuirTexto()">Disminuir</button>
<button onclick="restaurarTexto()">Normal</button>
```

**Desde JavaScript:**
```javascript
// Funciones disponibles
aumentarTexto();
disminuirTexto();
restaurarTexto();

// Obtener información
accessibilityManager.getCurrentSize();      // px actual
accessibilityManager.getZoomPercentage();   // % de zoom

// Escuchar cambios
window.addEventListener('accessibilityChange', (event) => {
    console.log(`Nuevo tamaño: ${event.detail.fontSize}px`);
});

// Reinicializar después de AJAX
reinitializeAccessibility();
```

### 📚 Documentación Completa

Consulta estos archivos para más detalles:
- [Guía Completa](./ACCESSIBILITY_GUIDE.md)
- [Ejemplos y Personalizaciones](./ACCESSIBILITY_EXAMPLES.md)
- [Referencia Rápida](./ACCESSIBILITY_QUICK_REFERENCE.md)
- [Testing y Troubleshooting](./ACCESSIBILITY_TESTING.md)

---
```

## 📍 Dónde Agregar en README.md

**Opción 1:** Al final del README
```markdown
## ♿ ACCESIBILIDAD - Cambio de Tamaño de Texto
[... contenido de arriba ...]
```

**Opción 2:** En una sección de "Características"
```markdown
### Características
- ✅ Autenticación de usuarios
- ✅ Sistema de mapas interactivo
- ✅ **Accesibilidad con cambio de tamaño de texto**
```

**Opción 3:** En tabla de contenidos (si tiene)
```markdown
## Tabla de Contenidos
1. [Instalación](#instalación)
2. [Uso](#uso)
3. [Accesibilidad](#-accesibilidad---cambio-de-tamaño-de-texto)
4. [Contribuir](#contribuir)
```

---

## ✅ Verificación Post-Instalación

Después de agregar a README y hacer deploy:

### Checklist Local
- [ ] Servidor corre sin errores
- [ ] Botones aparecen en navbar
- [ ] Botones funcionan en escritorio
- [ ] Botones funcionan en móvil
- [ ] Tamaño persiste en localStorage
- [ ] No hay errores en console (F12)

### Checklist Pre-Producción
- [ ] `python manage.py collectstatic --noinput` ejecutado
- [ ] `accessibility.js` está en `STATIC_ROOT`
- [ ] `accessibility.css` está en `STATIC_ROOT`
- [ ] `base.html` tiene los includes correctos
- [ ] Testear en navegadores principales (Chrome, Firefox, Safari)
- [ ] Testear en móvil
- [ ] Testear con VPN/proxy (si aplica)

---

## 📌 Notas Importantes

1. **No borres archivos de accesibilidad** durante actualizaciones futuras
2. **No modifiques** `accessibility.js` a menos que sepas lo que haces
3. **Siempre ejecuta** `collectstatic` después de cambios en static/
4. **Testea bien** en diferentes navegadores antes de producción
5. **Mantén** los archivos de documentación (.md) para futuros desarrolladores

---

## 🔄 Próximas Mejoras (Roadmap)

- [ ] Guardar preferencias en DB para usuarios autenticados
- [ ] Agregar modo alto contraste
- [ ] Agregar modo lectura/focus
- [ ] Integración con atajos de teclado nativos del SO
- [ ] Modo oscuro nativo

---

## 📞 Soporte

Si tienes dudas o problemas:

1. Consulta los archivos de documentación
2. Abre consola (F12) y revisa errores
3. Verifica que `localStorage` esté habilitado
4. Prueba en navegador diferente para descartar compatibilidad

---

**Sistema de Accesibilidad - Listo para Producción ✅**
