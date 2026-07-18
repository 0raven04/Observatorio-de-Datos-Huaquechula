import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

# Create myapp_encuestacomercio table
cursor.execute("""
CREATE TABLE IF NOT EXISTS `myapp_encuestacomercio` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `fecha` DATETIME(6) NOT NULL,
    `tipo_comercio` VARCHAR(50) NOT NULL,
    `participacion_decisiones` SMALLINT UNSIGNED NOT NULL,
    `capacitacion_turistica` SMALLINT UNSIGNED NOT NULL,
    `integracion_turistica` SMALLINT UNSIGNED NOT NULL,
    `encuestador_id` INT NULL,
    CONSTRAINT `fk_encuestacomercio_encuestador`
        FOREIGN KEY (`encuestador_id`) REFERENCES `Encuestador` (`clave_encuestador`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

print("Table myapp_encuestacomercio created successfully!")

# Verify
cursor.execute("SHOW TABLES LIKE 'myapp_encuestacomercio'")
print("Exists:", cursor.fetchall())
