import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def fix():
    with connection.cursor() as cursor:
        # 1. Check Encuestador
        print("Checking Encuestador table...")
        cursor.execute("DESCRIBE Encuestador")
        columns = [col[0] for col in cursor.fetchall()]
        if 'id_usuario' not in columns:
            print("Adding id_usuario column to Encuestador...")
            cursor.execute("ALTER TABLE Encuestador ADD COLUMN id_usuario INT NOT NULL")
            # We assume the Usuario table exists and its PK is id_usuario
            # Try to add FK but ignore if it fails (might already be there or different constraint name)
            try:
                cursor.execute("ALTER TABLE Encuestador ADD CONSTRAINT fk_encuestador_usuario FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)")
            except:
                pass
            print("Column added successfully.")
        else:
            print("id_usuario already exists in Encuestador.")

        # 2. Check Indicador (myapp_indicador)
        print("Checking Indicador table...")
        cursor.execute("DESCRIBE myapp_indicador")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'data_source' not in columns:
            print("Adding data_source to Indicador...")
            cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN data_source VARCHAR(20) DEFAULT 'manual' NOT NULL")
        
        if 'inegi_indicator_id' not in columns:
            print("Adding inegi_indicator_id to Indicador...")
            cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN inegi_indicator_id VARCHAR(50) NULL")
            
        if 'last_sync' not in columns:
            print("Adding last_sync to Indicador...")
            cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN last_sync DATETIME(6) NULL")

    print("Database schema fix completed.")

if __name__ == "__main__":
    fix()
