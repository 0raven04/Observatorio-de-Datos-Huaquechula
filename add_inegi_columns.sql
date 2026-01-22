-- Script SQL para agregar columnas INEGI a la tabla de indicadores
-- Base de datos: observatorio_de_datos

USE observatorio_de_datos;

-- Agregar columnas para integración con INEGI
ALTER TABLE myapp_indicador ADD COLUMN inegi_indicator_id VARCHAR(50) NULL;
ALTER TABLE myapp_indicador ADD COLUMN data_source VARCHAR(20) DEFAULT 'manual';
ALTER TABLE myapp_indicador ADD COLUMN last_sync DATETIME NULL;

-- Verificar que las columnas se agregaron correctamente
DESCRIBE myapp_indicador;
