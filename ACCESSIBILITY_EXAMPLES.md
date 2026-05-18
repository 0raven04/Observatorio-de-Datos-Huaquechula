# 🎨 EJEMPLOS Y PERSONALIZACIONES - ACCESIBILIDAD

## Ejemplos Prácticos

### 1️⃣ Ajustar Dinámicamente Márgenes y Padding

```javascript
// En accessibility.js, agregar en método applyToElements()
applyToElements(size) {
    // ... código existente ...
    
    // Ajustar márgenes proporcionales al tamaño
    const marginPx = Math.max(8, (size - 14) * 0.5);
    document.querySelectorAll('.card, .container').forEach(el => {
        el.style.marginBottom = marginPx + 'px';
        el.style.paddingBottom = marginPx + 'px';
    });
}
```

### 2️⃣ Cambiar Alto de Línea (Line Height)

```javascript
// Agregar en applyToElements()
applyToElements(size) {
    // Calcular line-height basado en tamaño
    const lineHeight = 1.4 + (size > 20 ? 0.2 : 0);
    
    document.body.style.lineHeight = lineHeight;
    document.querySelectorAll('p, li, td, span').forEach(el => {
        el.style.lineHeight = lineHeight;
    });
}
```

### 3️⃣ Persistencia en Base de Datos (Django)

**models.py:**
```python
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    font_size_preference = models.IntegerField(default=16, choices=[
        (12, 'Pequeño'),
        (14, 'Normal'),
        (16, 'Mediano'),
        (18, 'Grande'),
        (20, 'Muy Grande'),
        (24, 'Extra Grande'),
    ])
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
```

**views.py:**
```python
from django.shortcuts import render
from .models import PerfilUsuario

def vista_inicio(request):
    font_size = 16  # default
    
    if request.user.is_authenticated:
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            font_size = perfil.font_size_preference
        except PerfilUsuario.DoesNotExist:
            pass
    
    context = {
        'font_size': font_size
    }
    return render(request, 'vista_inicio.html', context)
```

**base.html:**
```html
<script>
    // Aplicar tamaño guardado en DB si el usuario está autenticado
    {% if user.is_authenticated and font_size %}
        document.addEventListener('DOMContentLoaded', () => {
            if (accessibilityManager) {
                accessibilityManager.applyFontSize({{ font_size }});
            }
        });
    {% endif %}
</script>
```

**forms.py:**
```python
from django import forms
from .models import PerfilUsuario

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['font_size_preference']
        widgets = {
            'font_size_preference': forms.RadioSelect()
        }
```

### 4️⃣ Agregar Modo Alto Contraste

**accessibility.js - agregar a la clase:**
```javascript
class AccessibilityManager {
    constructor() {
        // ... código existente ...
        this.highContrastMode = false;
        this.initHighContrast();
    }
    
    initHighContrast() {
        const savedContrast = localStorage.getItem('observatorio_high_contrast');
        if (savedContrast === 'true') {
            this.enableHighContrast();
        }
    }
    
    enableHighContrast() {
        this.highContrastMode = true;
        document.body.style.filter = 'contrast(1.5)';
        document.documentElement.style.setProperty('--color-gris-oscuro', '#000');
        document.documentElement.style.setProperty('--color-arena-claro', '#fff');
        localStorage.setItem('observatorio_high_contrast', 'true');
    }
    
    disableHighContrast() {
        this.highContrastMode = false;
        document.body.style.filter = 'contrast(1)';
        document.documentElement.style.removeProperty('--color-gris-oscuro');
        document.documentElement.style.removeProperty('--color-arena-claro');
        localStorage.setItem('observatorio_high_contrast', 'false');
    }
    
    toggleHighContrast() {
        this.highContrastMode ? this.disableHighContrast() : this.enableHighContrast();
    }
}

// Función global
function toggleHighContrast() {
    if (accessibilityManager) accessibilityManager.toggleHighContrast();
}
```

**accessibility.css - agregar:**
```css
.accessibility-menu {
    /* ... código existente ... */
}

/* Botón de contraste alto */
.accessibility-contrast-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    min-height: 36px;
    padding: 6px 10px;
    border: 2px solid transparent;
    border-radius: 4px;
    background-color: transparent;
    color: inherit;
    cursor: pointer;
    font-size: calc(var(--font-size-base) - 2px);
    transition: all 0.2s ease;
}

.accessibility-contrast-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
}

.accessibility-contrast-btn.active {
    background-color: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
}
```

**base.html - agregar botón:**
```html
<div class="d-none d-md-flex ms-auto accessibility-menu text-white" style="margin-right: 15px;">
    <button class="accessibility-btn" id="accessibility-decrease" title="Disminuir texto" onclick="disminuirTexto()">
        <i class="fas fa-minus"></i>
    </button>
    <span class="accessibility-size-display" id="accessibility-size-display" title="Tamaño actual">100%</span>
    <button class="accessibility-btn" id="accessibility-increase" title="Aumentar texto" onclick="aumentarTexto()">
        <i class="fas fa-plus"></i>
    </button>
    <button class="accessibility-btn" title="Restaurar tamaño normal" onclick="restaurarTexto()">
        <i class="fas fa-redo"></i>
    </button>
    <!-- NUEVO: Botón de contraste alto -->
    <button class="accessibility-contrast-btn" title="Toggle contraste alto" onclick="toggleHighContrast()">
        <i class="fas fa-adjust"></i>
    </button>
</div>
```

### 5️⃣ Modo Lectura/Focus

```javascript
// Agregar a accessibility.js
class AccessibilityManager {
    // ... código existente ...
    
    enableReadingMode() {
        // Ocultar elementos distractivos
        document.querySelectorAll('.sidebar, .ads, .chat-widget').forEach(el => {
            el.style.display = 'none';
        });
        
        // Expandir contenido principal
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.maxWidth = '100%';
            mainContent.style.margin = '0';
        }
        
        // Aumentar espaciado entre líneas
        document.body.style.lineHeight = '1.8';
        
        // Guardar preferencia
        localStorage.setItem('observatorio_reading_mode', 'true');
        
        console.log('✓ Modo lectura habilitado');
    }
    
    disableReadingMode() {
        document.querySelectorAll('.sidebar, .ads, .chat-widget').forEach(el => {
            el.style.display = '';
        });
        
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.maxWidth = '';
            mainContent.style.margin = '';
        }
        
        document.body.style.lineHeight = '1.6';
        localStorage.setItem('observatorio_reading_mode', 'false');
        
        console.log('✓ Modo lectura deshabilitado');
    }
}

function toggleReadingMode() {
    if (accessibilityManager) {
        const isEnabled = localStorage.getItem('observatorio_reading_mode') === 'true';
        isEnabled ? accessibilityManager.disableReadingMode() : accessibilityManager.enableReadingMode();
    }
}
```

### 6️⃣ Integración con Eventos Personalizados

```javascript
// En tu archivo JS personalizado
window.addEventListener('accessibilityChange', (event) => {
    const fontSize = event.detail.fontSize;
    
    // Ejemplo: Ajustar canvas de Leaflet
    if (window.map) {
        map.invalidateSize();
    }
    
    // Ejemplo: Reajustar gráficos
    if (window.chartInstances) {
        window.chartInstances.forEach(chart => {
            chart.resize();
        });
    }
    
    // Ejemplo: Notificar al usuario
    console.log(`Tamaño de fuente cambió a: ${fontSize}px`);
});
```

### 7️⃣ Guardar Múltiples Preferencias

```javascript
// Crear objeto de preferencias
const AccessibilityPreferences = {
    save(key, value) {
        const prefs = JSON.parse(localStorage.getItem('observatorio_prefs') || '{}');
        prefs[key] = value;
        localStorage.setItem('observatorio_prefs', JSON.stringify(prefs));
    },
    
    load(key, defaultValue) {
        const prefs = JSON.parse(localStorage.getItem('observatorio_prefs') || '{}');
        return prefs[key] || defaultValue;
    },
    
    remove(key) {
        const prefs = JSON.parse(localStorage.getItem('observatorio_prefs') || '{}');
        delete prefs[key];
        localStorage.setItem('observatorio_prefs', JSON.stringify(prefs));
    },
    
    clear() {
        localStorage.removeItem('observatorio_prefs');
    }
};

// Uso
AccessibilityPreferences.save('fontSize', 18);
AccessibilityPreferences.save('highContrast', true);
AccessibilityPreferences.save('readingMode', false);

// Cargar
const fontSize = AccessibilityPreferences.load('fontSize', 16);
```

### 8️⃣ API AJAX para Django

**urls.py:**
```python
from django.urls import path
from . import views

urlpatterns = [
    # ... rutas existentes ...
    path('api/accessibility/save/', views.save_accessibility_preference, name='save_accessibility'),
    path('api/accessibility/get/', views.get_accessibility_preference, name='get_accessibility'),
]
```

**views.py:**
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@require_http_methods(["POST"])
@csrf_exempt  # En producción, usa CSRF token
def save_accessibility_preference(request):
    try:
        data = json.loads(request.body)
        font_size = data.get('fontSize', 16)
        
        # Guardar en sesión o DB
        request.session['font_size_preference'] = font_size
        
        return JsonResponse({'status': 'success', 'fontSize': font_size})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["GET"])
def get_accessibility_preference(request):
    font_size = request.session.get('font_size_preference', 16)
    return JsonResponse({'fontSize': font_size})
```

**accessibility.js - modificado:**
```javascript
applyFontSize(size) {
    // ... código existente ...
    
    // Guardar en servidor vía AJAX
    if (window.user && window.user.authenticated) {
        fetch('/api/accessibility/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ fontSize: size })
        }).then(r => r.json()).catch(e => console.warn('No se pudo guardar en servidor:', e));
    }
}
```

### 9️⃣ Teclado Shortcuts

```javascript
// Agregar a accessibility.js
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Más = Aumentar
    if ((e.ctrlKey || e.metaKey) && (e.key === '+' || e.key === '=')) {
        e.preventDefault();
        aumentarTexto();
    }
    
    // Ctrl/Cmd + Menos = Disminuir
    if ((e.ctrlKey || e.metaKey) && (e.key === '-' || e.key === '_')) {
        e.preventDefault();
        disminuirTexto();
    }
    
    // Ctrl/Cmd + 0 = Restaurar
    if ((e.ctrlKey || e.metaKey) && e.key === '0') {
        e.preventDefault();
        restaurarTexto();
    }
});
```

### 🔟 Detectar Preferencias del Sistema

```javascript
// Detectar preferencia de usuario por texto grande
const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
const prefersHighContrast = window.matchMedia('(prefers-contrast: more)').matches;
const prefersLargerText = window.matchMedia('(prefers-reduced-motion: no-preference)').matches;

if (prefersHighContrast) {
    console.log('El usuario prefiere alto contraste');
    // Aplicar automáticamente
}

if (window.matchMedia('(prefers-font-size-large: true)').matches) {
    // Algunos navegadores soportan esto
    accessibilityManager.applyFontSize(18);
}
```

---

## 🎯 Casos de Uso Específicos

### Caso 1: Formularios Largos
```javascript
// Aumentar espaciado en inputs para formularios largos
document.querySelectorAll('form input, form textarea').forEach(el => {
    el.style.lineHeight = '1.8';
    el.style.marginBottom = '1.5rem';
});
```

### Caso 2: Tablas con Muchos Datos
```javascript
// Hacer tablas más legibles
document.querySelectorAll('table').forEach(table => {
    table.style.borderCollapse = 'collapse';
    table.querySelectorAll('td, th').forEach(cell => {
        cell.style.padding = '12px';
        cell.style.borderBottom = '1px solid #ddd';
    });
});
```

### Caso 3: Mapas Interactivos
```javascript
// Si usas Leaflet
window.addEventListener('accessibilityChange', (event) => {
    if (window.map) {
        // Actualizar tamaño de popups
        window.map.eachLayer(layer => {
            if (layer.getPopup) {
                const popup = layer.getPopup();
                if (popup) {
                    popup._updateContent();
                }
            }
        });
    }
});
```

### Caso 4: Múltiples Idiomas
```javascript
// Almacenar idioma junto con preferencias
class AccessibilityWithLanguage extends AccessibilityManager {
    constructor() {
        super();
        this.language = localStorage.getItem('language') || 'es';
    }
    
    getButtonLabel(action) {
        const labels = {
            es: { increase: 'Aumentar', decrease: 'Disminuir', reset: 'Normal' },
            en: { increase: 'Increase', decrease: 'Decrease', reset: 'Reset' },
        };
        return labels[this.language][action] || action;
    }
}
```

---

## 🚀 Checklist de Implementación

- [ ] Copiar `accessibility.js` a `myapp/static/myapp/JAV/`
- [ ] Copiar `accessibility.css` a `myapp/static/myapp/CSS/`
- [ ] Actualizar `base.html` con includes
- [ ] Actualizar `base.css` con variables
- [ ] Ejecutar `python manage.py collectstatic --noinput`
- [ ] Probar en desktop y móvil
- [ ] Probar con diferentes navegadores
- [ ] Verificar localStorage
- [ ] Verificar Leaflet popups (si aplica)
- [ ] Documentar en README

---

**¿Necesitas más ejemplos? Pide específicamente lo que quieras implementar.**
