DROP DATABASE IF EXISTS observatorio_de_datos;
CREATE DATABASE observatorio_de_datos;
USE observatorio_de_datos;

CREATE TABLE Usuario(
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ap VARCHAR(100) NOT NULL,
    am VARCHAR(100),
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'encuestador', 'propietario') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


CREATE TABLE Encuestador(
    id_usuario INT,
    clave_encuestador INT AUTO_INCREMENT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Propietario(
    id_usuario INT,
    clave_propietario INT AUTO_INCREMENT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Administrador(
    id_usuario INT,
    clave_admin INT AUTO_INCREMENT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE Registro_visita (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    estancia_dias TINYINT UNSIGNED DEFAULT 1,
    visitas_previas TINYINT UNSIGNED DEFAULT 1,
    motivo_visita ENUM('turismo', 'negocios', 'visita_familiar', 'estudios', 'otros') DEFAULT 'turismo',
    tipo_transporte ENUM('automovil', 'autobus', 'avion', 'tren', 'otros') DEFAULT 'automovil',
    procedencia VARCHAR(100),
    pais_origen VARCHAR(100),
    es_extranjero BOOLEAN DEFAULT FALSE,
    id_encuestador INT NOT NULL,
    mujeres_0_15 TINYINT UNSIGNED DEFAULT 0,
    mujeres_16_30 TINYINT UNSIGNED DEFAULT 0,
    mujeres_31_45 TINYINT UNSIGNED DEFAULT 0,
    mujeres_46_60 TINYINT UNSIGNED DEFAULT 0,
    mujeres_61_75 TINYINT UNSIGNED DEFAULT 0,
    mujeres_76_mas TINYINT UNSIGNED DEFAULT 0,
    hombres_0_15 TINYINT UNSIGNED DEFAULT 0,
    hombres_16_30 TINYINT UNSIGNED DEFAULT 0,
    hombres_31_45 TINYINT UNSIGNED DEFAULT 0,
    hombres_46_60 TINYINT UNSIGNED DEFAULT 0,
    hombres_61_75 TINYINT UNSIGNED DEFAULT 0,
    hombres_76_mas TINYINT UNSIGNED DEFAULT 0,
    FOREIGN KEY (id_encuestador) REFERENCES Encuestador(clave_encuestador) ON DELETE RESTRICT
) ENGINE=InnoDB;



CREATE TABLE ArchivoKMZ (
    id_archivo INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    archivo_path VARCHAR(500),
    descripcion TEXT,
    tamanio BIGINT DEFAULT 0,
    hash_archivo VARCHAR(64) NULL,
    tipo_archivo VARCHAR(10) DEFAULT 'kmz',
    procesado BOOLEAN DEFAULT FALSE,
    error_procesamiento TEXT,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
    procesado_en DATETIME NULL,
    visible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id_usuario)
);

CREATE TABLE GeometriaEspacial (
    id_geometria INT AUTO_INCREMENT PRIMARY KEY,
    id_archivo INT NULL, 
    nombre VARCHAR(255),
    tipo VARCHAR(20) NOT NULL,
    coordenadas JSON NOT NULL,
    centroide POINT NULL SRID 4326, 
    propiedades JSON,
    estilo JSON,
    perimetro DECIMAL(15, 6) NULL,
    area DECIMAL(15, 6) NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_archivo) REFERENCES ArchivoKMZ(id_archivo) ON DELETE CASCADE
);

CREATE TABLE Punto_Interes (
    id_punto INT AUTO_INCREMENT PRIMARY KEY,
    id_geometria INT NULL, 
    categoria ENUM('ofrenda', 'servicio', 'sitio_turistico', 'evento', 'otro') NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion MEDIUMTEXT,
    imagen_portada MEDIUMTEXT, 
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,
    hora_apertura TIME NULL,
    hora_cierre TIME NULL,
    dias_semana SET('lunes','martes','miercoles','jueves','viernes','sabado','domingo') NULL,
    usuario_creacion INT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_geometria) REFERENCES GeometriaEspacial(id_geometria) ON DELETE SET NULL,
    FOREIGN KEY (usuario_creacion) REFERENCES Usuario(id_usuario),
) ENGINE=InnoDB;


CREATE TABLE Ofrenda (
    id_ofrenda INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT NOT NULL UNIQUE,
    anfitrion VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Servicio (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT NOT NULL UNIQUE,
    tipo_servicio ENUM('cajero', 'hospedaje', 'modulo', 'salud') NOT NULL, 
    contacto VARCHAR(100),
    tipo_pago SET('efectivo','tarjeta', 'transferencia', 'ninguno') DEFAULT 'efectivo',  
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE Categoria_Sitio (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE, 
    codigo_slug VARCHAR(50) NOT NULL UNIQUE 
);

CREATE TABLE Sitio_turistico (
    id_sitio INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT NOT NULL UNIQUE,
    id_categoria INT NOT NULL,
    reglas_acceso TEXT, 
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES Categoria_Sitio(id_categoria)
) ENGINE=InnoDB;

CREATE TABLE Ruta (
    id_ruta INT AUTO_INCREMENT PRIMARY KEY,
    id_geometria INT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion MEDIUMTEXT,
    duracion_estimada INT,
    longitud_km DECIMAL(8,2),
    dificultad ENUM('facil', 'moderada', 'dificil') DEFAULT 'moderada',
    clave_propietario INT,
    estado ENUM('activa', 'inactiva') DEFAULT 'activa',
    FOREIGN KEY (id_geometria) REFERENCES GeometriaEspacial(id_geometria) ON DELETE SET NULL,
    FOREIGN KEY (clave_propietario) REFERENCES Propietario(clave_propietario)
) ENGINE=InnoDB;

CREATE TABLE Ruta_Detalle (
    id_ruta_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_ruta INT NOT NULL,
    id_punto INT NOT NULL,
    orden INT NOT NULL,
    tiempo_parada INT,
    actividad_sugerida TEXT,
    FOREIGN KEY (id_ruta) REFERENCES Ruta(id_ruta) ON DELETE CASCADE,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Galeria_Multimedia (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT NOT NULL, 
    url_archivo MEDIUMTEXT NOT NULL,
    tipo_archivo ENUM('imagen', 'video', 'audio') DEFAULT 'imagen',
    descripcion TEXT,
    es_portada BOOLEAN DEFAULT FALSE,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE
) ENGINE=InnoDB;