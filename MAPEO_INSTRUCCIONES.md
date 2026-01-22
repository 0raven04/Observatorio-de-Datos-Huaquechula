# Instrucciones para Completar el Mapeo de Indicadores INEGI

## Problema Actual

Las migraciones de Django no están agregando correctamente las columnas necesarias a la tabla `myapp_indicador`.

## Solución

### Opción 1: Ejecutar SQL Directamente (Más Rápido)

Abre phpMyAdmin o tu cliente MySQL y ejecuta:

```sql
USE observatorio_de_datos;

ALTER TABLE myapp_indicador ADD COLUMN inegi_indicator_id VARCHAR(50) NULL;
ALTER TABLE myapp_indicador ADD COLUMN data_source VARCHAR(20) DEFAULT 'manual';
ALTER TABLE myapp_indicador ADD COLUMN last_sync DATETIME NULL;
```

Luego ejecuta:
```bash
python map_indicators.py
```

### Opción 2: Desde Línea de Comandos MySQL

```bash
mysql -u root -p observatorio_de_datos

# Dentro de MySQL:
ALTER TABLE myapp_indicador ADD COLUMN inegi_indicator_id VARCHAR(50) NULL;
ALTER TABLE myapp_indicador ADD COLUMN data_source VARCHAR(20) DEFAULT 'manual';
ALTER TABLE myapp_indicador ADD COLUMN last_sync DATETIME NULL;
exit;

# Luego:
python map_indicators.py
```

## Resultado Esperado

El script `map_indicators.py` mapeará los 42 indicadores:
- **~20 indicadores** se mapearán a IDs de INEGI (datos demográficos oficiales)
- **~22 indicadores** se marcarán como datos locales (patrimonio, turismo comunitario)

## Siguiente Paso

Después del mapeo exitoso, podrás sincronizar datos reales:
```bash
python manage.py sync_inegi
```
