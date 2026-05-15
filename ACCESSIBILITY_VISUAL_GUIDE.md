# 🎨 GUÍA VISUAL - CÓMO SE VE LA ACCESIBILIDAD

## 📱 VISTA DESKTOP (≥768px)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🏛️ Logo    Inicio   Mapa   Encuesta ▼   Repositorio    [−][100%][+][⟲]  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                                          ↑ Aquí están
                                                          los botones

Navbar oscuro con fondo (#333)
Botones con iconos de Font Awesome
Fondo semi-transparente para botones
Animación suave al pasar mouse
```

### Botones Individuales

```
┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐
│ [−]     │  │ 100%     │  │ [+]     │  │ [⟲]     │
│ Menos   │  │ Tamaño   │  │ Más     │  │ Restaurar
└─────────┘  └──────────┘  └─────────┘  └─────────┘
   16px        14px           16px         16px
```

**Comportamiento:**
- Hover: Fondo más opaco + escala pequeña
- Click: Animación de pulso
- Deshabilitado: Opacidad 50%, cursor not-allowed

---

## 📲 VISTA MÓVIL (<768px)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🏛️ Logo        ☰ Menú   ┃ ← Navbar compacto
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛

(El usuario hace click en ☰)

┏━━━━━━━━━━━━━━━━━━━━━━━┓
┃ × Menú                 ┃
├────────────────────────┤
┃ 🏠 Inicio              ┃
┃ 🗺️ Mapa                ┃
┃ 📋 Encuesta ▼          ┃
┃ 📚 Repositorio         ┃
│────────────────────────│
┃ ♿ Accesibilidad       ┃
├────────────────────────┤
┃ [− Disminuir]          ┃
┃ [⟲ Normal]  [+ Aumentar] ┃
┃ Tamaño actual: 100%    ┃
└────────────────────────┘
        ↑ Nueva sección
```

---

## 🔢 ESCALA DE TAMAÑOS

```
Tipo de Contenido    | 12px | 14px | 16px | 18px | 20px | 24px
─────────────────────┼──────┼──────┼──────┼──────┼──────┼──────
Títulos (h1)         | 20   | 22   | 24   | 26   | 28   | 32
Títulos (h2)         | 18   | 20   | 22   | 24   | 26   | 30
Párrafos             | 12   | 14   | 16   | 18   | 20   | 24
Botones              | 11   | 13   | 15   | 17   | 19   | 23
Tablas               | 11   | 13   | 15   | 17   | 19   | 23
Navbar               | 11   | 13   | 15   | 17   | 19   | 23
─────────────────────┴──────┴──────┴──────┴──────┴──────┴──────

Ejemplo: Si usuario aumenta a 20px
- Párrafos: 20px
- h1: 28px
- h2: 26px
- Botones: 19px
```

---

## 🎯 CAMBIOS VISUALES ANTES/DESPUÉS

### ANTES (16px normal)

```
┌──────────────────────────┐
│ Título Principal         │ ← 24px
├──────────────────────────┤
│ Este es un párrafo       │ ← 16px
│ que explica algo         │
│ de forma normal.         │
│                          │
│ [Botón]  [Cancelar]      │ ← 15px
└──────────────────────────┘
```

### DESPUÉS (24px máximo)

```
┌────────────────────────────────────────┐
│ Título Principal                       │ ← 32px (más grande)
├────────────────────────────────────────┤
│ Este es un párrafo que explica algo    │ ← 24px (más legible)
│ de forma normal pero ahora es más      │
│ fácil de leer.                         │ ← 24px
│                                        │
│ [Botón]  [Cancelar]                    │ ← 23px (más visible)
└────────────────────────────────────────┘
```

---

## 🎬 ANIMACIÓN DE CAMBIO

```
Usuario click [+]
      ↓
transition: font-size 0.2s ease;
      ↓
Animación suave de crecimiento
      ↓
Todos los textos crecen simultáneamente
      ↓
Sin parpadeos ni saltos bruscos
      ↓
Completada en 200ms
```

---

## 💾 FLUJO DE DATOS

```
┌─────────────────────────────────┐
│ Usuario click en botón          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ JavaScript ejecuta función      │
│ aumentarTexto() / disminuirTexto│
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ AccessibilityManager calcula    │
│ nuevo tamaño (16 → 18)          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Aplica variables CSS en :root   │
│ --font-size-base: 18px;         │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Aplica styles inline en elementos
│ h1 { font-size: 26px }          │
│ p { font-size: 18px }           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Guarda en localStorage          │
│ observatorio_font_size: "18"    │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Dispara evento accessibilityChange
│ Los otros scripts pueden responder
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Actualiza UI del botón          │
│ Desactiva [+] si está en máximo │
└─────────────────────────────────┘
```

---

## 📊 INDICADOR VISUAL

```
Mínimo (12px)      Normal (16px)      Máximo (24px)
     │                   │                   │
     ▼                   ▼                   ▼
├────────┼────────────────┼────────────────┤
0%                    50%                 100%

Mostrado como: "50%" o "100%"
```

---

## 🎨 COLORES

### Navbar (Dark)
```
Fondo: #333 (Dark Bootstrap)
Botones: transparent
Hover: rgba(255,255,255,0.2)
Texto: #fff (blanco)
Borde: rgba(255,255,255,0.3)
```

### Móvil (Offcanvas)
```
Fondo: text-bg-dark (Bootstrap)
Botones: btn-outline-light
Texto: text-white
```

### Animación
```
Hover: background-color 0.3s ease
Click: transform scale(0.98)
```

---

## ⌚ ESTADOS DEL BOTÓN

### Estado Normal
```
┌─────────┐
│ [+]     │  Cursor: pointer
└─────────┘  Opacidad: 1
             Escala: 1
```

### Estado Hover
```
┌──────────┐
│  [+]     │  Cursor: pointer
└──────────┘  Opacidad: 1
              Escala: 1.05
              Fondo: rgba(255,255,255,0.2)
```

### Estado Active/Click
```
┌────────┐
│ [+]    │  Cursor: pointer
└────────┘  Opacidad: 1
            Escala: 0.98
            Animación: pulse
```

### Estado Deshabilitado (En máximo o mínimo)
```
┌─────────┐
│ [+]     │  Cursor: not-allowed
└─────────┘  Opacidad: 0.5
             Escala: 1
             No responde a clicks
```

---

## 📍 POSICIÓN EN PANTALLA

### Desktop
```
X: 100% - 160px (margenes)
Y: Top of navbar
Z-index: auto (navegación normal)
```

### Móvil
```
En offcanvas, dentro del menú
Bajo la sección de navegación
Sobre el footer del menú
```

---

## 🔤 TIPOGRAFÍA DEL MENÚ

```
Botones:
- Font size: variable (16px base)
- Font weight: 600
- Font family: Font Awesome + Segoe UI

Display de % :
- Font size: 14px
- Font weight: 600
- Font family: Segoe UI
```

---

## 🎯 ÁREA DE CLICKEO

```
Botón individual:
┌──────────────────┐
│ Área clickeable  │ 36px × 36px (mínimo)
│   [−]            │
│                  │
└──────────────────┘

Distancia entre botones: 6px (gap)
```

---

## 🌐 COMPATIBILIDAD VISUAL

```
Chrome  ✅ Colores precisos
Firefox ✅ Animaciones suaves
Safari  ✅ Renderizado correcto
Edge    ✅ Compatibilidad total
Móvil   ✅ Touch optimizado
```

---

## 🎬 EJEMPLO DE USO COMPLETO

```
1. Página carga → Botones en navbar → Tamaño: 100%
                   [−] | 100% | [+] | [⟲]

2. Usuario click [+]
   → Transición suave (200ms)
   → Tamaño aumenta a 105%
   → Todos los textos crecen
   → Botones se actualizan

3. Usuario click [+] de nuevo
   → Tamaño 110%
   → Más cambios visuales

4. Usuario click [⟲]
   → Vuelta inmediata a 100%
   → Restaura posición original

5. Usuario cierra navegador
   → Preferencia guardada en localStorage

6. Usuario vuelve mañana
   → Página carga con tamaño guardado (110%)
   → Sin necesidad de reajustar
```

---

## 🎓 CONCLUSIÓN

El sistema es:
- ✅ **Visual:** Cambios obvios e inmediatos
- ✅ **Accesible:** Fácil de encontrar y usar
- ✅ **Responsive:** Funciona en todas las pantallas
- ✅ **Suave:** Animaciones sin saltos
- ✅ **Persistente:** Se recuerda la preferencia
- ✅ **Compatible:** Todos los navegadores

**Listo para producción.** 🚀
