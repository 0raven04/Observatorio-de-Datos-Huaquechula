from django.db import migrations

def recreate_encuestainstitucional(apps, schema_editor):
    if schema_editor.connection.vendor == 'mysql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS `myapp_encuestacomercio`")
            cursor.execute("DROP TABLE IF EXISTS `myapp_encuestainstitucional`")
            cursor.execute("""
                CREATE TABLE `myapp_encuestainstitucional` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `fecha` datetime(6) NOT NULL,
                    `registro_pci` smallint unsigned NOT NULL,
                    `canales_difusion` json NOT NULL,
                    `mecanismos_regulacion` smallint unsigned NOT NULL,
                    `plan_desarrollo` smallint unsigned NOT NULL,
                    `porcentaje_comunidades` smallint unsigned NOT NULL,
                    `encuestador_id` int(11) DEFAULT NULL,
                    PRIMARY KEY (`id`),
                    KEY `fk_institucional_enc` (`encuestador_id`),
                    CONSTRAINT `fk_institucional_enc` FOREIGN KEY (`encuestador_id`) REFERENCES `Encuestador` (`clave_encuestador`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
            """)

def reverse_migration(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('myapp', '0009_final_sync'),
    ]

    operations = [
        migrations.RunPython(recreate_encuestainstitucional, reverse_migration),
    ]
