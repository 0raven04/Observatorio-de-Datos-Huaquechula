

DROP DATABASE IF EXISTS observatorio_de_datos;
CREATE DATABASE observatorio_de_datos;
USE observatorio_de_datos;

CREATE TABLE Usuario(
    id_usuario INT AUTO_INCREMENT NOT NULL, 
    nombre VARCHAR(50), -- MULTIVALUADO
    nombre_usuario TINYTEXT NOT NULL, 
    email VARCHAR(50) NOT NULL, 
    contrasenia VARCHAR(20)
 ) ENGINE=innodb;

CREATE TABLE Administrador(
    clave_admin INT AUTO_INCREMENT NOT NULL
) ENGINE=innodb;

CREATE TABLE Encuestador(
	clave_encuestador INT AUTO_INCREMENT NOT NULL
) ENGINE=innodb;

CREATE TABLE Propietario(
	clave_propietario INT AUTO_INCREMENT NOT NULL
) ENGINE=innodb;

CREATE TABLE Documento(
    id_documento INT AUTO_INCREMENT NOT NULL,
    titulo VARCHAR(20),
    fecha_carga DATETIME,
    descripcion MEDIUMTEXT,
    url MEDIUMTEXT NOT NULL, 
    fecha_actualizacion DATETIME, -- MULTIVALUADO
    clasificacion VARCHAR(50) -- ENUM
) ENGINE=innodb;

CREATE TABLE Registro_visita(
    id_registro INT AUTO_INCREMENT NOT NULL,
    fecha DATE,
    edad TINYINT,
    sexo ENUM('Hombre','Mujer'), 
    tamanio_grupo TINYINT,
    numero_visitas TINYINT, -- AUTOCALCULADO
    estancia_esperada ENUM('1','2-3','3-5','5 o mas'),  
    motivo_visita ENUM('vacacion','ocio','trabajo','visita familiar', 'otro'), 
    tipo_hospedaje ENUM('no se hospeda','hotel','casa de conocido'), 
    tipo_transporte ENUM('publico','privado'),
    procedencia VARCHAR(50)
) ENGINE=innodb;

CREATE TABLE Grafico(
    id_grafico INT AUTO_INCREMENT NOT NULL,
    tipo VARCHAR(50), -- ENUM
    parametros VARCHAR(50) -- Multivaluado
) ENGINE=innodb;

CREATE TABLE genera(
    id_grafico INT NOT NULL,
    id_registro INT NOT NULL
) ENGINE=innodb;

	

CREATE TABLE Ofrenda(
    clave_ofrenda INT AUTO_INCREMENT NOT NULL,
    anfitrion VARCHAR(50),
    nombre VARCHAR(50) 
) ENGINE=innodb;

CREATE TABLE Servicio(
    clave_servicio INT AUTO_INCREMENT NOT NULL,
    categoria  VARCHAR(50), -- ENUM
    contacto  VARCHAR(10) -- Multivaluado
) ENGINE=innodb;

CREATE TABLE Sitio_turistico(
    clave_ST INT AUTO_INCREMENT NOT NULL,
    categoria  VARCHAR(50), -- ENUM
    contacto  VARCHAR(50) -- Multivaluado
) ENGINE=innodb;

	

CREATE TABLE Ruta(
    id_ruta INT AUTO_INCREMENT NOT NULL, 
    nombre VARCHAR(50), 
    duracion TIME, -- AUTOCALCULADO
    longitud FLOAT, -- AUTOCALCULADO
    clasificacion VARCHAR(50), -- ENUM
    descripcion MEDIUMTEXT
) ENGINE=innodb;


CREATE TABLE Ubicacion (
    id_Ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255),
    calle VARCHAR(100),
    altitud DECIMAL(10, 6),
    latitud DECIMAL(10, 6),
    longitud DECIMAL(10, 6),
    descripcion MEDIUMTEXT
) ENGINE=innodb;

CREATE TABLE Punto_Interes (
    id_punto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    descripcion TEXT,
    tipo_pago ENUM('efectivo','tarjeta'),
    descripcion MEDIUMTEXT,
    id_Ubicacion INT,
    FOREIGN KEY (id_Ubicacion) REFERENCES Ubicacion(id_Ubicacion) ON DELETE SET NULL
)ENGINE=innodb;


CREATE TABLE Fotografia (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT,
    ruta_archivo VARCHAR(255),
    descripcion VARCHAR(255),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_punto) REFERENCES Punto_Interes(id_punto)
) ENGINE=innodb;


-- PRIMARY KEYS

ALTER TABLE Usuario
ADD CONSTRAINT PK_Usuario PRIMARY KEY (id_usuario,LastName,email);

ALTER TABLE Administrador
ADD PRIMARY KEY (clave_admin);

ALTER TABLE Encuestador
ADD PRIMARY KEY (clave_encuestador);

ALTER TABLE Propietario
ADD PRIMARY KEY (clave_propietario);

ALTER TABLE Documento
ADD CONSTRAINT PK_Documento PRIMARY KEY (id_documento,LastName,email);

ALTER TABLE Registro_visita
ADD PRIMARY KEY (id_registro);

ALTER TABLE Grafico
ADD PRIMARY KEY (id_grafico);

ALTER TABLE genera
ADD CONSTRAINT PK_genera PRIMARY KEY (id_grafico,id_registro);

ALTER TABLE Punto_interes
ADD PRIMARY KEY (id_punto);

ALTER TABLE Ofrenda
ADD PRIMARY KEY (clave_ofrenda);

ALTER TABLE Servicio
ADD PRIMARY KEY (clave_servicio);

ALTER TABLE Sitio_turistico
ADD PRIMARY KEY (clave_ST);

ALTER TABLE Ubicacion
ADD PRIMARY KEY (id_ubicacion);

ALTER TABLE Ruta
ADD PRIMARY KEY (id_ruta);

-- FOREIGN KEYS

ALTER TABLE Documento
ADD FOREIGN KEY (FK_Administrador) REFERENCES Administrador(clave_admin) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Registro_visita
ADD FOREIGN KEY (FK_Encuestador) REFERENCES Encuestador(clave_encuestador) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Ruta
ADD FOREIGN KEY (FK_Punto_Interes) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Ubicacion
ADD FOREIGN KEY (FK_Punto_Interes) REFERENCES Punto_Interes(id_punto) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE genera
ADD CONSTRAINT FK_Grafico
FOREIGN KEY (id_grafico) REFERENCES Grafico(id_grafico)ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Fotografia
ADD CONSTRAINT FK_Registro
FOREIGN KEY (id_registro) REFERENCES Registro(id_registro)ON DELETE CASCADE ON UPDATE CASCADE;