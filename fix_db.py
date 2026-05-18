import mysql.connector
import os

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="observatorio_de_datos"
    )
    cursor = conn.cursor()

    # 1. Add id_usuario to Encuestador if missing
    print("Checking Encuestador table...")
    cursor.execute("DESCRIBE Encuestador")
    columns = [col[0] for col in cursor.fetchall()]
    if 'id_usuario' not in columns:
        print("Adding id_usuario column to Encuestador...")
        # Since it's a OneToOneField to Usuario(id_usuario), we need to match the type (int)
        cursor.execute("ALTER TABLE Encuestador ADD COLUMN id_usuario INT NOT NULL")
        cursor.execute("ALTER TABLE Encuestador ADD CONSTRAINT fk_encuestador_usuario FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)")
        print("Column added successfully.")
    else:
        print("id_usuario already exists in Encuestador.")

    # 2. Add data_source, inegi_indicator_id, last_sync to Indicador if missing
    print("Checking Indicador table...")
    cursor.execute("DESCRIBE myapp_indicador")
    columns = [col[0] for col in cursor.fetchall()]
    
    if 'data_source' not in columns:
        print("Adding data_source to Indicador...")
        cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN data_source VARCHAR(20) DEFAULT 'manual'")
    
    if 'inegi_indicator_id' not in columns:
        print("Adding inegi_indicator_id to Indicador...")
        cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN inegi_indicator_id VARCHAR(50) NULL")
        
    if 'last_sync' not in columns:
        print("Adding last_sync to Indicador...")
        cursor.execute("ALTER TABLE myapp_indicador ADD COLUMN last_sync DATETIME NULL")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database fix completed.")

except Exception as e:
    print(f"Error: {e}")
