# ⚡ INICIO RÁPIDO - 5 MINUTOS

## 🎯 Tu Meta: Tener accesibilidad funcionando en tu app

---

## ✅ PASO 1: Verificar Archivos (1 minuto)

Abre una terminal en la raíz del proyecto:

```bash
# Verificar que existan
ls myapp/static/myapp/JAV/accessibility.js
ls myapp/static/myapp/CSS/accessibility.css
```

**Resultado esperado:**
```
myapp/static/myapp/JAV/accessibility.js
myapp/static/myapp/CSS/accessibility.css
```

✅ Si ves ambas rutas → SIGUIENTE PASO

❌ Si no existen → Error, contacta soporte

---

## ✅ PASO 2: Recolectar Estáticos (1 minuto)

**ESTO ES CRÍTICO** ⚠️

```bash
python manage.py collectstatic --noinput
```

**Resultado esperado:**
```
Copying '...\accessibility.js'
Copying '...\accessibility.css'
...
X static files copied
```

✅ Si ves "copied" → SIGUIENTE PASO

❌ Si hay errores → Verifica permisos de carpeta

---

## ✅ PASO 3: Reiniciar Servidor (30 segundos)

```bash
# Ctrl+C si está corriendo
# Luego:
python manage.py runserver
```

**Resultado esperado:**
```
Starting development server at http://127.0.0.1:8000/
```

✅ Si arranca sin errores → SIGUIENTE PASO

❌ Si hay errores en la consola → Revisa ACCESSIBILITY_TESTING.md

---

## ✅ PASO 4: Abrir Navegador (1 minuto)

Abre http://localhost:8000

### Desktop
Mira en la **esquina superior derecha del navbar**

**Debes ver:** `[−] | 100% | [+] | [⟲]`

✅ Si ves los botones → Está funcionando

❌ Si NO los ves → Limpiar caché (Ctrl+Shift+Del)

### Móvil/Responsive
Abre menú ☰ → Busca "♿ Accesibilidad"

**Debes ver:** 3 botones con etiquetas

✅ Si ves los botones → Está funcionando

---

## ✅ PASO 5: Probar Funcionamiento (1 minuto)

### Test 1: Hacer click
1. Click en `[+]` → Todo debe hacerse más grande
2. Click en `[+]` → Aún más grande
3. Click en `[−]` → Debe disminuir
4. Click en `[⟲]` → Debe volver a normal

✅ Si funciona → Excelente

### Test 2: Persistencia
1. Aumenta el tamaño a máximo
2. **Recarga la página** (F5)
3. Debe mantener el tamaño máximo

✅ Si se mantiene → Perfecto

### Test 3: Sin Errores
1. Abre DevTools (F12)
2. Click en "Console"
3. **No debe haber errores rojo**

✅ Si está limpia → Listo para producción

---

## 🎉 ¡LISTO!

**Tu sistema de accesibilidad está funcionando**

---

## ¿Qué Sigue?

### Opción A: Usar tal como está
✅ Está listo para producción
✅ Funciona en desktop y móvil
✅ Guarda preferencias
✅ Completamente funcional

### Opción B: Personalizar
Consulta: **ACCESSIBILITY_EXAMPLES.md**
- Cambiar límites de tamaño
- Agregar modo alto contraste
- Integrar con base de datos
- Etc.

### Opción C: Desplegar a Producción
Consulta: **ACCESSIBILITY_DEPLOYMENT_CHECKLIST.md**

---

## 🆘 Ayuda Rápida

| Problema | Solución |
|----------|----------|
| Botones no aparecen | Ejecutar `collectstatic --noinput` |
| No funciona | Limpiar caché (Ctrl+Shift+Del) |
| Error en consola | Ver ACCESSIBILITY_TESTING.md |
| En móvil no se ve | Abrir menú ☰ completamente |

---

## 📚 Documentación

Tienes acceso a:
- ✅ `ACCESSIBILITY_SUMMARY.md` - Resumen ejecutivo
- ✅ `ACCESSIBILITY_QUICK_REFERENCE.md` - Referencia rápida
- ✅ `ACCESSIBILITY_GUIDE.md` - Guía completa
- ✅ `ACCESSIBILITY_EXAMPLES.md` - Ejemplos
- ✅ `ACCESSIBILITY_TESTING.md` - Testing guide
- ✅ `ACCESSIBILITY_DEPLOYMENT_CHECKLIST.md` - Para producción

---

## ✨ Características

Tus usuarios ahora pueden:
- ✅ Aumentar/disminuir texto
- ✅ La preferencia se recuerda
- ✅ Funciona sin recargar
- ✅ Sincroniza entre pestañas
- ✅ Compatible con todos los navegadores

---

## 🚀 PRODUCCIÓN

Cuando quieras desplegar:

```bash
# Mismo proceso
python manage.py collectstatic --noinput
# Deploy normalmente
# Verificar con F12 que no haya errores
```

**Listo.**

---

**¿Tienes dudas?** → Consulta ACCESSIBILITY_QUICK_REFERENCE.md

**¿Código no funciona?** → Consulta ACCESSIBILITY_TESTING.md

**¿Quieres personalizar?** → Consulta ACCESSIBILITY_EXAMPLES.md

---

**Tiempo total: 5 minutos ⏱️**

**Accesibilidad global: ✅ ACTIVADA**
