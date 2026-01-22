# Guía de Integración con la API del INEGI

## Configuración Inicial

### 1. Obtener Token de Acceso

1. Visita: https://www.inegi.org.mx/app/api/indicadores/
2. Regístrate como desarrollador
3. Obtén tu token de acceso
4. Copia el token

### 2. Configurar el Token

Opción A - Variable de entorno (Recomendado para producción):
```bash
# Windows PowerShell
$env:INEGI_API_TOKEN="tu_token_aqui"

# Linux/Mac
export INEGI_API_TOKEN="tu_token_aqui"
```

Opción B - Archivo .env:
```bash
# Crea un archivo .env en la raíz del proyecto
INEGI_API_TOKEN=tu_token_aqui
```

Opción C - Directamente en settings.py (Solo para desarrollo):
```python
INEGI_API_TOKEN = 'tu_token_aqui'
```

## Uso del Servicio

### Sincronizar Datos desde Terminal

```bash
# Ver ayuda
python manage.py sync_inegi --help

# Simular sincronización (no guarda cambios)
python manage.py sync_inegi --dry-run

# Sincronizar todos los indicadores
python manage.py sync_inegi

# Sincronizar un indicador específico
python manage.py sync_inegi --indicator-id 5
```

### Usar el Servicio en Código Python

```python
from myapp.services.inegi_service import get_inegi_service

# Obtener instancia del servicio
service = get_inegi_service()

if service:
    # Consultar un indicador específico
    data = service.fetch_indicator_data('1002000001')  # Población total
    
    # data = {'2020': 12345, '2021': 12400, ...}
    for periodo, valor in data.items():
        print(f"{periodo}: {valor}")
```

## IDs de Indicadores INEGI Disponibles

### Salud
- `6207019048` - Esperanza de vida al nacer
- `6207019049` - Tasa de mortalidad infantil

### Educación
- `6207019050` - Grado promedio de escolaridad

### Población
- `1002000001` - Población total

### Pobreza
- `6200240364` - Población en situación de pobreza

## Código Geográfico de Huaquechula

- **Estado**: Puebla = `21`
- **Municipio**: Huaquechula = `071`
- **Código completo**: `21071`

## Estructura de Respuesta de la API

```json
{
  "Series": [{
    "OBSERVATIONS": [
      {
        "TIME_PERIOD": "2020",
        "OBS_VALUE": "12345"
      }
    ],
    "UNIT": "Personas",
    "NOTE": "Nota sobre el indicador"
  }]
}
```

## Próximos Pasos

1. ✅ Obtener token del INEGI
2. ✅ Configurar token en el proyecto
3. ⏳ Mapear indicadores locales con IDs de INEGI
4. ⏳ Ejecutar sincronización inicial
5. ⏳ Configurar sincronización automática (cron/celery)
