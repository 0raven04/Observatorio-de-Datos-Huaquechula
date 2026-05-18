# ✅ DEPLOYMENT CHECKLIST - ACCESIBILIDAD GLOBAL

## PRE-DEPLOYMENT (Local)

### 1. Verificación de Archivos
- [ ] `myapp/static/myapp/JAV/accessibility.js` existe
- [ ] `myapp/static/myapp/CSS/accessibility.css` existe
- [ ] Ambos archivos contienen código (no vacíos)
- [ ] `myapp/templates/base.html` modificado
- [ ] `myapp/static/myapp/CSS/base.css` tiene variables CSS

```bash
# Script de verificación
ls -lh myapp/static/myapp/JAV/accessibility.js
ls -lh myapp/static/myapp/CSS/accessibility.css
grep "font-size-base" myapp/static/myapp/CSS/base.css
grep "accessibility.js" myapp/templates/base.html
```

### 2. Testing Local
- [ ] Servidor corre sin errores: `python manage.py runserver`
- [ ] No hay errores en consola (F12)
- [ ] Botones visibles en navbar
- [ ] Botones funcionan al clickear
- [ ] Tamaño persiste (recarga página)

```bash
# Recolectar estáticos (OBLIGATORIO)
python manage.py collectstatic --noinput
```

- [ ] Comando ejecutó sin errores
- [ ] Archivos copiados a `STATIC_ROOT`

### 3. Testing Navegadores
- [ ] Chrome/Chromium: OK
- [ ] Firefox: OK
- [ ] Safari: OK
- [ ] Edge: OK

### 4. Testing Dispositivos
- [ ] Desktop (1920x1080): OK
- [ ] Tablet (768px): OK
- [ ] Móvil (375px): OK
- [ ] Botones funcionan en todos

### 5. Testing Funcionalidad
- [ ] [−] Disminuye correctamente
- [ ] [+] Aumenta correctamente
- [ ] [⟲] Restaura a 16px
- [ ] Indicador muestra % correcto
- [ ] localStorage guarda valor

```javascript
// En consola verificar
localStorage.getItem('observatorio_font_size')
// Debe devolver número entre 12-24
```

- [ ] Sincronización entre pestañas (abrir 2 pestañas)
- [ ] Cambios en Tab1 se reflejan en Tab2

### 6. Testing de Elementos
- [ ] Títulos cambian tamaño
- [ ] Párrafos cambian
- [ ] Botones cambian
- [ ] Inputs cambian
- [ ] Tablas cambian (si existen)
- [ ] Cards cambian (si existen)
- [ ] Navbar cambia
- [ ] Footer cambia
- [ ] Chat widget cambia (si existe)
- [ ] Mapas se actualizan (si existen)

### 7. Testing de Límites
- [ ] No puede disminuir menos de 12px
- [ ] No puede aumentar más de 24px
- [ ] Botones se deshabilitan en límites
- [ ] Mensaje de límite alcanzado (opcional)

---

## DEPLOYMENT (Staging/Pre-prod)

### 1. Configuración
- [ ] `DEBUG = False` en settings.py
- [ ] `STATIC_URL` configurado correctamente
- [ ] `STATIC_ROOT` existe y es accesible
- [ ] `ALLOWED_HOSTS` incluye dominios

```bash
# En servidor staging
python manage.py collectstatic --noinput
```

- [ ] Comando ejecutó sin errores
- [ ] Archivos en lugar correcto

### 2. Testing en Staging
- [ ] Accesibilidad funciona completamente
- [ ] No hay errores 404 en estáticos
- [ ] Botones visibles y funcionales
- [ ] localStorage funciona
- [ ] Sin errores en consola del navegador

### 3. Performance
- [ ] Tiempo de carga < 2 segundos
- [ ] Sin bloqueadores de script
- [ ] Sin warnings en DevTools
- [ ] Memory usage normal

### 4. Seguridad
- [ ] HTTPS habilitado
- [ ] CSRF token presente
- [ ] Sin console errors
- [ ] Sin vulnerabilidades XSS

### 5. Documentación
- [ ] README.md actualizado con sección de accesibilidad
- [ ] Archivos .md de documentación en repositorio
- [ ] Comentarios en código
- [ ] Changelog actualizado

---

## DEPLOYMENT (Producción)

### 1. Pre-deployment
- [ ] Backup actual de la base de datos
- [ ] Backup actual de archivos estáticos
- [ ] Rama creada en git para rollback
- [ ] Equipo notificado del cambio

### 2. Deployment
```bash
# En producción
git pull origin main  # O tu rama

# Recolectar estáticos (CRÍTICO)
python manage.py collectstatic --noinput

# Reiniciar servicios
systemctl restart gunicorn
systemctl restart nginx
# O tu stack de deployment
```

- [ ] Deployment completado sin errores
- [ ] Logs revisados para verificar

### 3. Post-deployment Inmediato
- [ ] Sitio responde (HTTP 200)
- [ ] Botones de accesibilidad visibles
- [ ] Botones funcionan
- [ ] Sin errores en consola (F12)
- [ ] localStorage funciona

### 4. Post-deployment (Primeras Horas)
- [ ] Monitoreo de errores activo
- [ ] Logs del servidor monitoreados
- [ ] Usuarios informan sobre accesibilidad
- [ ] Performance normal
- [ ] No hay spikes en CPU/memoria

### 5. Post-deployment (Primer Día)
- [ ] Funcionalidad completa verificada
- [ ] Usuarios satisfechos
- [ ] No hay reportes de bugs
- [ ] Estadísticas de uso normales

---

## ROLLBACK (Si es necesario)

```bash
# Revertir cambios
git revert HEAD
git push origin main

# Recolectar estáticos nuevamente
python manage.py collectstatic --noinput

# Reiniciar servicios
systemctl restart gunicorn
systemctl restart nginx

# Verificar
# Accesibilidad debe desaparecer
```

- [ ] Rollback completado
- [ ] Sitio funciona normalmente
- [ ] Usuarios notificados

---

## LISTA DE VERIFICACIÓN RÁPIDA

### ✅ Mínimo para Deployment

```
[ ] 1. Archivos existen
[ ] 2. collectstatic ejecutado
[ ] 3. Botones visibles
[ ] 4. Botones funcionan
[ ] 5. localStorage funciona
[ ] 6. Sin errores en consola
[ ] 7. Sincronización OK
[ ] 8. Responsive OK
[ ] 9. HTTPS OK
[ ] 10. Performance OK
```

Si todos estos están ✅, puedes desplegar.

---

## COMANDOS ÚTILES

### Local
```bash
# Limpiar y recolectar estáticos
python manage.py collectstatic --clear --noinput

# Verificar estáticos
find myapp/static -name "accessibility.*"

# Iniciar en modo debug
python manage.py runserver --debug-toolbar

# Testing
python manage.py test myapp

# Migrations
python manage.py migrate
```

### Producción
```bash
# SSH al servidor
ssh user@production.com

# Navegar a proyecto
cd /path/to/project

# Recolectar estáticos
python manage.py collectstatic --noinput

# Reiniciar gunicorn
systemctl restart gunicorn

# Ver logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/error.log

# Verificar salud
curl https://tu-dominio.com

# Revisar en navegador
# Abre DevTools (F12)
# Ve a Console
# No debe haber errores
```

---

## MONITOREO POST-DEPLOYMENT

### Errores a Monitorear
- [ ] 404 en archivos estáticos
- [ ] JavaScript errors en consola
- [ ] localStorage errors
- [ ] CORS errors (si aplica)
- [ ] Performance degradation

### Métricas
- [ ] Acceso a la funcionalidad
- [ ] Clics en botones
- [ ] localStorage writes
- [ ] Event dispatches

```javascript
// Para monitoreo (opcional)
window.addEventListener('accessibilityChange', (e) => {
    // Enviar a analytics si lo deseas
    console.log('Accessibility changed:', e.detail);
});
```

---

## NOTIFICACIÓN A USUARIOS

### Email/Anuncio
```
🎉 Nueva Característica: Accesibilidad

Ya puedes ajustar el tamaño de texto en toda la aplicación:
- Botones en navbar (escritorio)
- Menú accesibilidad (móvil)
- Tu preferencia se recuerda automáticamente

¿Cómo usar?
1. Desktop: Busca [−] [+] [⟲] en navbar
2. Móvil: Abre menú → Accesibilidad

Beneficios:
- Mayor legibilidad
- Acceso para personas con baja visión
- Preferencia guardada
- Sin recargar página

¿Preguntas? Contáctanos.
```

---

## DOCUMENTACIÓN PARA STAKEHOLDERS

### Para PM/Product
- ✅ Característica completamente implementada
- ✅ Código listo para producción
- ✅ WCAG AA compatible
- ✅ Sin dependencias externas
- ✅ Código documentado
- ✅ Testing completado

### Para QA
- ✅ Testing guide: `ACCESSIBILITY_TESTING.md`
- ✅ Casos de uso: `ACCESSIBILITY_EXAMPLES.md`
- ✅ Visual guide: `ACCESSIBILITY_VISUAL_GUIDE.md`

### Para Dev Team
- ✅ Guía completa: `ACCESSIBILITY_GUIDE.md`
- ✅ Referencia rápida: `ACCESSIBILITY_QUICK_REFERENCE.md`
- ✅ Código comentado
- ✅ Ejemplos incluidos

---

## HORARIO RECOMENDADO DE DEPLOYMENT

- ✅ Martes-Jueves 10:00-14:00 (peak support time)
- ✅ Después de testing completo
- ✅ No viernes antes de fin de semana
- ✅ No antes de eventos importantes

---

## CONTACTOS DE EMERGENCIA

```
Frontend Lead: [nombre]
Backend Lead: [nombre]
DevOps: [nombre]
Product: [nombre]
```

---

## POST-DEPLOYMENT REPORT

**Fecha:** _______________
**Hora de inicio:** _______________
**Hora de finalización:** _______________
**Responsable:** _______________

**Status:** [ ] Exitoso [ ] Con Issues [ ] Rollback

**Issues encontrados:**
- 
- 
- 

**Usuarios afectados:** _______________

**Acciones tomadas:**
- 
- 
- 

**Seguimiento necesario:**
- 
- 
- 

---

## AUTORIZACIÓN

- [ ] Product Owner: _____ Fecha: _____
- [ ] Tech Lead: _____ Fecha: _____
- [ ] DevOps: _____ Fecha: _____

---

**Deployment Checklist - Accesibilidad Global**
**Versión 1.0**
**Fecha de creación: 2025-05-15**
