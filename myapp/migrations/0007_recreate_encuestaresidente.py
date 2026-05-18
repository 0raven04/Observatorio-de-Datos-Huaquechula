# Custom migration to replace EncuestaResidente schema

from django.db import migrations


def recreate_encuestaresidente(apps, schema_editor):
    """Drop and recreate the EncuestaResidente table with the new schema."""
    if schema_editor.connection.vendor == 'mysql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS `myapp_encuestaresidente`")
            cursor.execute("""
                CREATE TABLE `myapp_encuestaresidente` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `fecha` datetime(6) NOT NULL,
                    `edad` smallint unsigned NOT NULL,
                    `genero` varchar(15) NOT NULL,
                    `barrio_colonia` varchar(100) NOT NULL,
                    `alteracion_rutina` smallint unsigned NOT NULL,
                    `acceso_servicios_festividades` smallint unsigned NOT NULL,
                    `desvirtuacion_tradicion` smallint unsigned NOT NULL,
                    `participacion_preservacion` smallint unsigned NOT NULL,
                    `participacion_decisiones` smallint unsigned NOT NULL,
                    `capacitacion_turistica` smallint unsigned NOT NULL,
                    `beneficio_economico` smallint unsigned NOT NULL,
                    `encuestador_id` int(11) DEFAULT NULL,
                    PRIMARY KEY (`id`),
                    KEY `fk_residente_enc` (`encuestador_id`),
                    CONSTRAINT `fk_residente_enc` FOREIGN KEY (`encuestador_id`) REFERENCES `encuestador` (`clave_encuestador`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
            """)


def reverse_migration(apps, schema_editor):
    """Cannot reverse — old data is lost."""
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('myapp', '0006_encuestavisitante'),
    ]

    operations = [
        migrations.RunPython(recreate_encuestaresidente, reverse_migration),
    ]
