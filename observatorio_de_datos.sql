-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 01-11INSERT-2025 a las 14:10:08
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `observatorio_de_datos`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add encuestador', 7, 'add_encuestador'),
(26, 'Can change encuestador', 7, 'change_encuestador'),
(27, 'Can delete encuestador', 7, 'delete_encuestador'),
(28, 'Can view encuestador', 7, 'view_encuestador'),
(29, 'Can add usuario', 8, 'add_usuario'),
(30, 'Can change usuario', 8, 'change_usuario'),
(31, 'Can delete usuario', 8, 'delete_usuario'),
(32, 'Can view usuario', 8, 'view_usuario'),
(33, 'Can add registro visita', 9, 'add_registrovisita'),
(34, 'Can change registro visita', 9, 'change_registrovisita'),
(35, 'Can delete registro visita', 9, 'delete_registrovisita'),
(36, 'Can view registro visita', 9, 'view_registrovisita'),
(37, 'Can add persona visita', 10, 'add_personavisita'),
(38, 'Can change persona visita', 10, 'change_personavisita'),
(39, 'Can delete persona visita', 10, 'delete_personavisita'),
(40, 'Can view persona visita', 10, 'view_personavisita');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user`
--

CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, '1234', NULL, 1, 'kevin', 'Admin', 'User', 'admin@correo.com', 1, 1, '2025-08-26 22:06:03.000000'),
(2, '', '2025-11-01 13:09:11.962475', 0, 'kevin2', '', '', '', 0, 1, '2025-08-27 04:18:21.567355'),
(3, '', '2025-11-01 13:09:04.705185', 1, 'kevin3', '', '', '', 1, 1, '2025-08-27 04:19:58.288593');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'permission'),
(3, 'auth', 'group'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(7, 'myapp', 'encuestador'),
(10, 'myapp', 'personavisita'),
(9, 'myapp', 'registrovisita'),
(8, 'myapp', 'usuario'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-08-27 03:59:22.060097'),
(2, 'auth', '0001_initial', '2025-08-27 03:59:22.373064'),
(3, 'admin', '0001_initial', '2025-08-27 03:59:22.448625'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-08-27 03:59:22.455648'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-08-27 03:59:22.463455'),
(6, 'contenttypes', '0002_remove_content_type_name', '2025-08-27 03:59:22.507515'),
(7, 'auth', '0002_alter_permission_name_max_length', '2025-08-27 03:59:22.544019'),
(8, 'auth', '0003_alter_user_email_max_length', '2025-08-27 03:59:22.556519'),
(9, 'auth', '0004_alter_user_username_opts', '2025-08-27 03:59:22.563923'),
(10, 'auth', '0005_alter_user_last_login_null', '2025-08-27 03:59:22.593893'),
(11, 'auth', '0006_require_contenttypes_0002', '2025-08-27 03:59:22.597083'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2025-08-27 03:59:22.606398'),
(13, 'auth', '0008_alter_user_username_max_length', '2025-08-27 03:59:22.620786'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2025-08-27 03:59:22.636536'),
(15, 'auth', '0010_alter_group_name_max_length', '2025-08-27 03:59:22.652847'),
(16, 'auth', '0011_update_proxy_permissions', '2025-08-27 03:59:22.661894'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2025-08-27 03:59:22.676867'),
(18, 'myapp', '0001_initial', '2025-08-27 03:59:22.823451'),
(19, 'myapp', '0002_auto_20250826_2131', '2025-08-27 03:59:22.899207'),
(20, 'sessions', '0001_initial', '2025-08-27 03:59:22.929817');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('479hycv2pfbwohdpactz6jh1sqlf6lm7', '.eJxVjMsKwjAURP8layl5XdO69B-6DsnNDQliWppkIeK_24KCrgbmnJkns663ZHulzebALkyx02_nHd6oHOD-cOs6HIRKy-haXsoXD3PtbsvL9WP_XSRX074XArUOQDJGPQJxP6I2iJFHCYK44goEyiinaLgBPZ1RaArgjVRyD8Feb6woON0:1uuuiM:Gqculldhpqau1jHP3xUShbOdRdS9n54D31WfVZnXKKA', '2025-09-20 15:20:30.829373'),
('5mmgcbztqnp91ek9ltffut3agul2c4wk', '.eJxVjMsKwjAURP8layl5XdO69B-6DsnNDQliWppkIeK_24KCrgbmnJkns663ZHulzebALkyx02_nHd6oHOD-cOs6HIRKy-haXsoXD3PtbsvL9WP_XSRX074XArUOQDJGPQJxP6I2iJFHCYK44goEyiinaLgBPZ1RaArgjVRyD8Feb6woON0:1v19zS:AnRl3jFzJKQe2SS0KusMTOAYpnNnSIrf4Yonbmax04s', '2025-10-07 20:51:58.514817'),
('jprs93kbqs48hjiiw3dpgnjc5p6dpsa5', '.eJxVjEEKwyAURO_iugT9ak267B2yFv1-UUpNiLoopXdvAi20q4F5b-bJrOst2V5pszmwCwN2-u28wxuVA9wfbl2Hg1BpGV3LS_niYa7dbXm5fuy_i-Rq2vdCoFJBE8SoRk3cj6gMYuQRtCAuudQCIcIUDTdaTWcUioL2BiTsIdjrDauNONw:1uw3mB:m-uOvLteM4APSJiWXoKcj3E4w-Yd2mf9u9g3fTLIuG0', '2025-09-23 19:13:11.767451'),
('nzafhfdxinucbz3dg1ii760f9rqodt3w', '.eJxVjMsKwjAURP8layl5XdO69B-6DsnNDQliWppkIeK_24KCrgbmnJkns663ZHulzebALkyx02_nHd6oHOD-cOs6HIRKy-haXsoXD3PtbsvL9WP_XSRX074XArUOQDJGPQJxP6I2iJFHCYK44goEyiinaLgBPZ1RaArgjVRyD8Feb6woON0:1vFAyz:8bnugLpCWQlWB8BnCPvh94BROPVnWtJJG2CHQhpCsmc', '2025-11-15 12:45:25.370711'),
('wpjikz4051ejpo5t8xxpqvjemz0skf87', '.eJxVjEEKwyAURO_iugT9ak267B2yFv1-UUpNiLoopXdvAi20q4F5b-bJrOst2V5pszmwCwN2-u28wxuVA9wfbl2Hg1BpGV3LS_niYa7dbXm5fuy_i-Rq2vdCoFJBE8SoRk3cj6gMYuQRtCAuudQCIcIUDTdaTWcUioL2BiTsIdjrDauNONw:1vFBLz:JpRBfZMycRcyXV0dIue1nbvGr0iUggD6iwlkpKOSNBI', '2025-11-15 13:09:11.969847');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `encuestador`
--

CREATE TABLE IF NOT EXISTS `encuestador` (
  `clave_encuestador` varchar(50) NOT NULL,
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `encuestador`
--

INSERT INTO `encuestador` (`clave_encuestador`, `id_usuario`) VALUES
('2', 2),
('1', 3),
('ADMIN_4', 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona_visita`
--
CREATE TABLE IF NOT EXISTS `persona_visita` (
  `id_persona` int(11) NOT NULL,
  `edad` enum('0-15','16-30','31-45','46-60','61-75','75+') DEFAULT NULL,
  `sexo` varchar(10) NOT NULL,
  `id_registro` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `persona_visita`
--

INSERT INTO `persona_visita` (`id_persona`, `edad`, `sexo`, `id_registro`) VALUES
(9, '', 'Hombre', 11),
(14, '', 'Hombre', 17),
(15, '', 'Mujer', 17),
(16, '', 'Hombre', 20),
(17, '', 'Hombre', 20);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registro_visita`
--

CREATE TABLE IF NOT EXISTS `registro_visita` (
  `id_registro` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `tamanio_grupo` smallint(5) UNSIGNED NOT NULL CHECK (`tamanio_grupo` >= 0),
  `es_extranjero` tinyint(1) NOT NULL,
  `pais_origen` varchar(100) NOT NULL,
  `procedencia` varchar(50) NOT NULL,
  `tipo_transporte` varchar(10) DEFAULT NULL,
  `motivo_visita` varchar(20) DEFAULT NULL,
  `estancia_dias` smallint(5) UNSIGNED NOT NULL CHECK (`estancia_dias` >= 0),
  `numero_visitas` smallint(5) UNSIGNED NOT NULL CHECK (`numero_visitas` >= 0),
  `id_encuestador` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `registro_visita`
--

INSERT INTO `registro_visita` (`id_registro`, `fecha`, `tamanio_grupo`, `es_extranjero`, `pais_origen`, `procedencia`, `tipo_transporte`, `motivo_visita`, `estancia_dias`, `numero_visitas`, `id_encuestador`) VALUES
(9, '2025-08-29', 1, 1, 'Bahrain', 'puebla', 'Automovil', 'Turismo', 1, 1, '1'),
(10, '2025-08-30', 1, 1, 'Antarctica', 'puebla', 'Autobus', 'Trabajo', 1, 1, '1'),
(11, '2025-08-30', 1, 1, 'Afghanistan', 'puebla', 'Automovil', 'Turismo', 1, 1, 'ADMIN_4'),
(12, '2025-08-30', 1, 1, 'Bahrain', 'puebla', 'Automovil', 'Turismo', 1, 1, '1'),
(13, '2025-08-30', 1, 1, 'Algeria', 'Cuernavaca', 'Automovil', 'Turismo', 1, 1, '1'),
(14, '2025-08-30', 1, 1, 'Bahrain', 'Puebla', 'Autobus', 'Turismo', 1, 1, '1'),
(15, '2025-08-30', 1, 1, 'American Samoa', 'Puebla', 'Avion', 'Trabajo', 5, 5, '1'),
(16, '2025-08-30', 1, 1, 'Yemen', 'Cuernavaca', 'Automovil', 'Trabajo', 1, 1, '1'),
(17, '2025-08-30', 2, 1, 'Afghanistan', 'Cuernavaca', 'Automovil', 'Turismo', 11, 11, 'ADMIN_4'),
(18, '2025-08-30', 1, 1, 'Argentina', 'Puebla', 'Automovil', 'Turismo', 1, 1, '1'),
(19, '2025-09-05', 1, 1, 'Australia', '', 'Automovil', 'Estudios', 1, 1, '1'),
(20, '2025-09-05', 2, 1, 'Andorra', 'Cuernavaca', NULL, NULL, 11, 11, 'ADMIN_4'),
(21, '2025-09-06', 1, 1, 'Bahamas', 'puebla', 'Automovil', 'Trabajo', 1, 1, '1'),
(22, '2025-11-01', 3, 1, 'Bahamas', 'puebla', 'Autobus', 'Turismo', 1, 1, '1');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE IF NOT EXISTS `usuario` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `ap` varchar(50) NOT NULL,
  `am` varchar(50) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `email` varchar(254) NOT NULL,
  `contrasenia` varchar(255) NOT NULL,
  `tipo` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `nombre`, `ap`, `am`, `nombre_usuario`, `email`, `contrasenia`, `tipo`) VALUES
(1, 'kevin', 'arana', 'diaz', 'kevin', 'admin@correo.com', '1234', 'administrado'),
(2, 'Nuevo', 'ApellidoP', 'ApellidoM', 'usuario2', 'usuario2@example.com', '1234', 'encuestador'),
(3, 'Kevin2', 'Arana2', 'Diaz2', 'kevin2', 'kevin2@example.com', 'pbkdf2_sha256$260000$TYfEAbJk8KmZLCQiv8tegA$YKRXdnN8fXLS3vpotMvQ/Z26iYaMUivlRMASe04he/w=', 'encuestador'),
(4, 'Kevin3', 'Arana3', 'Diaz3', 'kevin3', 'kevin3@example.com', 'pbkdf2_sha256$260000$TgkBCxOu3hYC1f8mMJTxnO$h1b1NCOSzP5WdA5U/vcKMmQ041TQp04EzPuS7zJ2Qk4=', 'admin');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `encuestador`
--
ALTER TABLE `encuestador`
  ADD PRIMARY KEY (`clave_encuestador`),
  ADD UNIQUE KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `persona_visita`
--
ALTER TABLE `persona_visita`
  ADD PRIMARY KEY (`id_persona`),
  ADD KEY `Persona_visita_id_registro_fac265aa_fk_Registro_` (`id_registro`);

--
-- Indices de la tabla `registro_visita`
--
ALTER TABLE `registro_visita`
  ADD PRIMARY KEY (`id_registro`),
  ADD KEY `Registro_visita_id_encuestador_0c132ee3_fk_Encuestad` (`id_encuestador`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD 3PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `persona_visita`
--
ALTER TABLE `persona_visita`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `registro_visita`
--
ALTER TABLE `registro_visita`
  MODIFY `id_registro` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `encuestador`
--
ALTER TABLE `encuestador`
  ADD CONSTRAINT `Encuestador_id_usuario_83201b4d_fk_Usuario_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

--
-- Filtros para la tabla `persona_visita`
--
ALTER TABLE `persona_visita`
  ADD CONSTRAINT `Persona_visita_id_registro_fac265aa_fk_Registro_` FOREIGN KEY (`id_registro`) REFERENCES `registro_visita` (`id_registro`);

--
-- Filtros para la tabla `registro_visita`
--
ALTER TABLE `registro_visita`
  ADD CONSTRAINT `Registro_visita_id_encuestador_0c132ee3_fk_Encuestad` FOREIGN KEY (`id_encuestador`) REFERENCES `encuestador` (`clave_encuestador`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
