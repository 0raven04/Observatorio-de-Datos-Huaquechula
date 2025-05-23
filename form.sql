DROP DATABASE IF EXISTS observatorio_de_datos;
CREATE DATABASE observatorio_de_datos;
USE observatorio_de_datos;

-- Tablas principales
CREATE TABLE Usuario(
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    ap VARCHAR(50),
    am VARCHAR(50),
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE, 
    email VARCHAR(50) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL UNIQUE, 
    tipo ENUM('admin', 'encuestador', 'propietario') NOT NULL
) ENGINE=InnoDB;


CREATE TABLE Administrador(
    clave_admin VARCHAR(50) PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Encuestador(
    id_usuario INT PRIMARY KEY,
    clave_encuestador VARCHAR(50) UNIQUE,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Propietario(
    id_usuario INT PRIMARY KEY,
    clave_propietario VARCHAR(50) UNIQUE,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Documento(
    id_documento INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP,
    descripcion MEDIUMTEXT,
    url MEDIUMTEXT NOT NULL,
    fecha_actualizacion DATETIME,
    clasificacion ENUM('publico', 'privado', 'confidencial'),
    id_admin INT,
    FOREIGN KEY (id_admin) REFERENCES Administrador(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE Registro_visita(
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE DEFAULT CURRENT_DATE,
    edad TINYINT,
    sexo ENUM('Hombre','Mujer','Otro'),
    tamanio_grupo TINYINT DEFAULT 1,
    numero_visitas TINYINT DEFAULT 1,
    estancia_esperada ENUM('1','2-3','3-5','5 o mas'),
    motivo_visita ENUM('vacacion','ocio','trabajo','visita familiar', 'otro'),
    tipo_transporte ENUM('Automovil','Autobus', 'Otro'),
    procedencia VARCHAR(50),
    id_encuestador INT,
    FOREIGN KEY (id_encuestador) REFERENCES Encuestador(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE Grafico(
    id_grafico INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('barras', 'lineas', 'pastel', 'mapa'),
    parametros JSON -- Mejor que VARCHAR para datos complejos
) ENGINE=InnoDB;

CREATE TABLE genera(
    id_grafico INT NOT NULL,
    id_registro INT NOT NULL,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_grafico, id_registro),
    FOREIGN KEY (id_grafico) REFERENCES Grafico(id_grafico) ON DELETE CASCADE,
    FOREIGN KEY (id_registro) REFERENCES Registro_visita(id_registro) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Ubicacion (
    id_Ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    descripcion MEDIUMTEXT,
    calle VARCHAR(100),
    altitud DECIMAL(10, 6),
    latitud DECIMAL(10, 6),
    longitud DECIMAL(10, 6)
) ENGINE=InnoDB;

CREATE TABLE Punto_Interes (
    id_punto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    tipo_pago ENUM('efectivo','tarjeta'),
    descripcion MEDIUMTEXT,
    id_Ubicacion INT,
    FOREIGN KEY (id_Ubicacion) REFERENCES Ubicacion(id_Ubicacion) ON DELETE SET NULL
)ENGINE=innodb;


CREATE TABLE Fotografia (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto)
) ENGINE=innodb;


CREATE TABLE Ofrenda(
    clave_ofrenda INT AUTO_INCREMENT PRIMARY KEY,
    anfitrion VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    id_registro INT,
    id_punto INT,
    FOREIGN KEY (id_registro) REFERENCES Registro_visita(id_registro),
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto)
) ENGINE=InnoDB;

CREATE TABLE Servicio(
    clave_servicio INT AUTO_INCREMENT PRIMARY KEY,
    categoria ENUM('restaurante', 'transporte', 'hospedaje', 'guia'),
    contacto VARCHAR(100),
    id_punto INT,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto)
) ENGINE=InnoDB;

CREATE TABLE Sitio_turistico(
    clave_ST INT AUTO_INCREMENT PRIMARY KEY,
    categoria ENUM('historico', 'natural', 'cultural', 'religioso'),
    contacto VARCHAR(100),
    id_punto INT,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto)
) ENGINE=InnoDB;

CREATE TABLE Ruta(
    id_ruta INT AUTO_INCREMENT PRIMARY KEY, 
    nombre VARCHAR(100) NOT NULL, 
    duracion TIME, 
    longitud FLOAT,
    clasificacion ENUM('facil', 'moderada', 'dificil'),
    descripcion MEDIUMTEXT,
    id_propietario INT,
    FOREIGN KEY (id_propietario) REFERENCES Propietario(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE Ruta_Puntos(
    id_ruta INT NOT NULL,
    id_punto INT NOT NULL,
    orden INT NOT NULL,
    PRIMARY KEY (id_ruta, id_punto),
    FOREIGN KEY (id_ruta) REFERENCES Ruta(id_ruta) ON DELETE CASCADE,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE
) ENGINE=InnoDB;