/**
 * geo_dinamico.js - Catálogo geográfico y lógica en cascada para procedencia/residencia
 * Diseñado para Observatorio de Datos Huaquechula (Web y clientes móviles)
 */

const PAISES_COMUNES = [
    "México",
    "Estados Unidos",
    "Canadá",
    "España",
    "Colombia",
    "Argentina",
    "Francia",
    "Alemania",
    "Reino Unido",
    "Brasil",
    "Chile",
    "Italia",
    "Japón",
    "China",
    "Guatemala",
    "Perú",
    "Costa Rica",
    "Otro país"
];

const DATOS_MEXICO = {
    "Puebla": [
        "Huaquechula",
        "Puebla de Zaragoza",
        "Atlixco",
        "San Pedro Cholula",
        "San Andrés Cholula",
        "Tehuacán",
        "Izúcar de Matamoros",
        "San Martín Texmelucan",
        "Cuautlancingo",
        "Amozoc",
        "Tepeaca",
        "Zacatlán",
        "Chignahuapan",
        "Huauchinango",
        "Teziutlán",
        "Tochimilco",
        "Atzitzihuacán",
        "Tianguismanalco",
        "Santa Isabel Cholula",
        "San Jerónimo Tecuanipan",
        "Calpan",
        "Chiautla de Tapia",
        "Acatlán de Osorio",
        "Tecamachalco",
        "Libres",
        "Otro municipio de Puebla"
    ],
    "Ciudad de México": [
        "Cuauhtémoc",
        "Coyoacán",
        "Benito Juárez",
        "Miguel Hidalgo",
        "Tlalpan",
        "Álvaro Obregón",
        "Iztapalapa",
        "Gustavo A. Madero",
        "Venustiano Carranza",
        "Azcapotzalco",
        "Xochimilco",
        "Iztacalco",
        "Cuajimalpa",
        "Magdalena Contreras",
        "Tláhuac",
        "Milpa Alta",
        "Otra alcaldía"
    ],
    "Estado de México": [
        "Toluca",
        "Ecatepec",
        "Naucalpan",
        "Tlalnepantla",
        "Nezahualcóyotl",
        "Metepec",
        "Chalco",
        "Valle de Chalco",
        "Chimalhuacán",
        "Ixtapaluca",
        "Texcoco",
        "Atizapán de Zaragoza",
        "Cuautitlán Izcalli",
        "Huixquilucan",
        "Amecameca",
        "Tepotzotlán",
        "Otro municipio del Edo. Mex."
    ],
    "Morelos": [
        "Cuernavaca",
        "Cuautla",
        "Jiutepec",
        "Temixco",
        "Tepoztlán",
        "Yautepec",
        "Jojutla",
        "Emiliano Zapata",
        "Ayala",
        "Yecapixtla",
        "Otro municipio de Morelos"
    ],
    "Tlaxcala": [
        "Tlaxcala de Xicohténcatl",
        "Apizaco",
        "Huamantla",
        "Chiautempan",
        "San Pablo del Monte",
        "Zacatelco",
        "Otro municipio de Tlaxcala"
    ],
    "Veracruz": [
        "Veracruz",
        "Xalapa",
        "Coatzacoalcos",
        "Córdoba",
        "Orizaba",
        "Poza Rica",
        "Boca del Río",
        "Minatitlán",
        "Tuxpan",
        "Papantla",
        "Otro municipio de Veracruz"
    ],
    "Oaxaca": [
        "Oaxaca de Juárez",
        "San Juan Bautista Tuxtepec",
        "Salina Cruz",
        "Juchitán de Zaragoza",
        "Santa Cruz Xoxocotlán",
        "Huajuapan de León",
        "Puerto Escondido",
        "Bahías de Huatulco",
        "Otro municipio de Oaxaca"
    ],
    "Guerrero": [
        "Acapulco de Juárez",
        "Chilpancingo",
        "Iguala de la Independencia",
        "Zihuatanejo",
        "Taxco de Alarcón",
        "Tlapa de Comonfort",
        "Otro municipio de Guerrero"
    ],
    "Hidalgo": [
        "Pachuca de Soto",
        "Tulancingo",
        "Tula de Allende",
        "Mineral de la Reforma",
        "Tizayuca",
        "Huejutla",
        "Otro municipio de Hidalgo"
    ],
    "Jalisco": [
        "Guadalajara",
        "Zapopan",
        "Tlaquepaque",
        "Tonalá",
        "Tlajomulco de Zúñiga",
        "Puerto Vallarta",
        "Lagos de Moreno",
        "Tepatitlán",
        "Otro municipio de Jalisco"
    ],
    "Nuevo León": [
        "Monterrey",
        "San Pedro Garza García",
        "Guadalupe",
        "San Nicolás de los Garza",
        "Apodaca",
        "Santa Catarina",
        "General Escobedo",
        "Santiago",
        "Otro municipio de Nuevo León"
    ],
    "Querétaro": [
        "Santiago de Querétaro",
        "San Juan del Río",
        "Corregidora",
        "El Marqués",
        "Tequisquiapan",
        "Jalpan de Serra",
        "Otro municipio de Querétaro"
    ],
    "Guanajuato": [
        "León",
        "Irapuato",
        "Celaya",
        "Salamanca",
        "Guanajuato",
        "San Miguel de Allende",
        "Silao",
        "Dolores Hidalgo",
        "Otro municipio de Guanajuato"
    ],
    "Michoacán": [
        "Morelia",
        "Uruapan",
        "Zamora",
        "Lázaro Cárdenas",
        "Pátzcuaro",
        "Zitácuaro",
        "Otro municipio de Michoacán"
    ],
    "Aguascalientes": ["Aguascalientes", "Jesús María", "Calvillo", "Rincón de Romos", "Otro municipio"],
    "Baja California": ["Tijuana", "Mexicali", "Ensenada", "Playas de Rosarito", "Tecate", "San Quintín", "Otro municipio"],
    "Baja California Sur": ["La Paz", "Los Cabos", "Cabo San Lucas", "San José del Cabo", "Loreto", "Comondú", "Otro municipio"],
    "Campeche": ["San Francisco de Campeche", "Ciudad del Carmen", "Champotón", "Escárcega", "Calkiní", "Otro municipio"],
    "Chiapas": ["Tuxtla Gutiérrez", "Tapachula", "San Cristóbal de las Casas", "Comitán de Domínguez", "Chiapa de Corzo", "Palenque", "Otro municipio"],
    "Chihuahua": ["Ciudad Juárez", "Chihuahua", "Cuauhtémoc", "Delicias", "Parral", "Nuevo Casas Grandes", "Otro municipio"],
    "Coahuila": ["Saltillo", "Torreón", "Monclova", "Piedras Negras", "Acuña", "Parras de la Fuente", "Otro municipio"],
    "Colima": ["Colima", "Manzanillo", "Villa de Álvarez", "Tecomán", "Otro municipio"],
    "Durango": ["Victoria de Durango", "Gómez Palacio", "Lerdo", "Santiago Papasquiaro", "Otro municipio"],
    "Nayarit": ["Tepic", "Bahía de Banderas", "Compostela", "Santiago Ixcuintla", "San Blas", "Otro municipio"],
    "Quintana Roo": ["Cancún (Benito Juárez)", "Playa del Carmen (Solidaridad)", "Chetumal (Othón P. Blanco)", "Cozumel", "Tulum", "Isla Mujeres", "Otro municipio"],
    "San Luis Potosí": ["San Luis Potosí", "Soledad de Graciano Sánchez", "Ciudad Valles", "Matehuala", "Rioverde", "Tamazunchale", "Otro municipio"],
    "Sinaloa": ["Culiacán", "Mazatlán", "Los Mochis (Ahome)", "Guasave", "Navolato", "Otro municipio"],
    "Sonora": ["Hermosillo", "Ciudad Obregón (Cajeme)", "Nogales", "San Luis Río Colorado", "Navojoa", "Guaymas", "Puerto Peñasco", "Otro municipio"],
    "Tabasco": ["Villahermosa (Centro)", "Cárdenas", "Comalcalco", "Huimanguillo", "Macuspana", "Paraíso", "Otro municipio"],
    "Tamaulipas": ["Reynosa", "Matamoros", "Nuevo Laredo", "Ciudad Victoria", "Tampico", "Ciudad Madero", "Altamira", "Otro municipio"],
    "Yucatán": ["Mérida", "Kanasín", "Valladolid", "Tizimín", "Progreso", "Izamal", "Otro municipio"],
    "Zacatecas": ["Zacatecas", "Guadalupe", "Fresnillo", "Jerez", "Sombrerete", "Otro municipio"]
};

/**
 * Inicializador del componente dinámico en cascada:
 * Configura los eventos de cambio y visibilidad asegurando compatibilidad con el backend.
 */
function initDynamicLocation(config) {
    const paisSelect = document.getElementById(config.paisSelectId);
    const estadoContainer = document.getElementById(config.estadoContainerId);
    const estadoSelect = document.getElementById(config.estadoSelectId);
    const ciudadContainer = document.getElementById(config.ciudadContainerId);
    const ciudadSelect = document.getElementById(config.ciudadSelectId);
    const ciudadInput = document.getElementById(config.ciudadInputId);
    const ciudadOtroContainer = config.ciudadOtroContainerId ? document.getElementById(config.ciudadOtroContainerId) : null;
    const ciudadOtroInput = config.ciudadOtroInputId ? document.getElementById(config.ciudadOtroInputId) : null;
    const consolidatedInput = config.consolidatedInputId ? document.getElementById(config.consolidatedInputId) : null;
    const previewEl = config.previewId ? document.getElementById(config.previewId) : null;

    if (!paisSelect) return;

    // 1. Llenar catálogo de Países si está vacío o solo tiene placeholder
    if (paisSelect.options.length <= 1) {
        paisSelect.innerHTML = '<option value="">Seleccione un país...</option>';
        PAISES_COMUNES.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p;
            opt.textContent = p;
            if (p === (config.defaultPais || "México")) {
                opt.selected = true;
            }
            paisSelect.appendChild(opt);
        });
    }

    // 2. Función para poblar Estados
    function poblarEstados() {
        if (!estadoSelect) return;
        estadoSelect.innerHTML = '<option value="">Seleccione un estado...</option>';
        Object.keys(DATOS_MEXICO).forEach(est => {
            const opt = document.createElement("option");
            opt.value = est;
            opt.textContent = est;
            if (config.defaultEstado && est === config.defaultEstado) {
                opt.selected = true;
            }
            estadoSelect.appendChild(opt);
        });
    }

    // 3. Función para poblar Ciudades
    function poblarCiudades(estado) {
        if (!ciudadSelect) return;
        ciudadSelect.innerHTML = '<option value="">Seleccione una ciudad / municipio...</option>';
        if (estado && DATOS_MEXICO[estado]) {
            DATOS_MEXICO[estado].forEach(cd => {
                const opt = document.createElement("option");
                opt.value = cd;
                opt.textContent = cd;
                if (config.defaultCiudad && cd === config.defaultCiudad) {
                    opt.selected = true;
                }
                ciudadSelect.appendChild(opt);
            });
        }
    }

    // 4. Actualizar valor consolidado y previsualización
    function updateConsolidated() {
        const pais = paisSelect.value;
        let previewText = "";
        let esExt = false;

        if (pais === "México" || pais === "Mexico") {
            const est = estadoSelect ? estadoSelect.value : "";
            let cd = ciudadSelect ? ciudadSelect.value : "";
            const isOtro = cd.startsWith("Otro ") || cd.startsWith("Otra ");
            
            if (isOtro && ciudadOtroInput && ciudadOtroInput.value.trim()) {
                cd = ciudadOtroInput.value.trim();
            } else if (isOtro) {
                cd = "";
            }

            if (cd && est) {
                previewText = `${cd}, ${est}`;
            } else if (cd) {
                previewText = cd;
            } else if (est) {
                previewText = est;
            } else {
                previewText = "México";
            }
            esExt = false;
        } else if (pais) {
            const cd = ciudadInput ? ciudadInput.value.trim() : "";
            if (cd) {
                previewText = `${cd}, ${pais}`;
            } else {
                previewText = pais;
            }
            esExt = true;
        } else {
            previewText = "";
            esExt = false;
        }

        if (consolidatedInput) {
            consolidatedInput.value = previewText;
        }
        if (previewEl) {
            previewEl.textContent = previewText || "No especificada";
        }
        if (config.esExtranjeroInputId) {
            const el = document.getElementById(config.esExtranjeroInputId);
            if (el) el.value = esExt ? "1" : "0";
        }
        if (config.esExtranjeroRadioName) {
            const val = esExt ? "1" : "0";
            const radio = document.querySelector(`input[name="${config.esExtranjeroRadioName}"][value="${val}"]`);
            if (radio) radio.checked = true;
        }
        if (config.paisOrigenInputId) {
            const el = document.getElementById(config.paisOrigenInputId);
            if (el) el.value = esExt ? pais : "";
        }
    }

    // 5. Manejador de cambio de País
    function onPaisChange() {
        const pais = paisSelect.value;
        const isMexico = (pais === "México" || pais === "Mexico");

        if (estadoContainer) {
            estadoContainer.style.display = isMexico ? "block" : "none";
        }
        if (ciudadContainer) {
            ciudadContainer.style.display = pais ? "block" : "none";
        }

        if (isMexico) {
            poblarEstados();
            if (config.defaultEstado) {
                poblarCiudades(config.defaultEstado);
            }

            if (estadoSelect) {
                if (config.estadoFieldName) {
                    estadoSelect.setAttribute("name", config.estadoFieldName);
                }
                estadoSelect.required = true;
            }

            if (ciudadSelect) {
                ciudadSelect.style.display = "block";
                if (config.ciudadFieldName) {
                    ciudadSelect.setAttribute("name", config.ciudadFieldName);
                }
                ciudadSelect.required = true;
            }
            if (ciudadInput) {
                ciudadInput.style.display = "none";
                ciudadInput.removeAttribute("name");
                ciudadInput.required = false;
                ciudadInput.value = "";
            }
            if (ciudadOtroContainer) {
                ciudadOtroContainer.style.display = "none";
                if (ciudadOtroInput) {
                    ciudadOtroInput.value = "";
                    ciudadOtroInput.removeAttribute("name");
                }
            }
        } else if (pais !== "") {
            // Extranjero
            if (estadoSelect) {
                if (config.estadoFieldName) {
                    // Si el backend requiere un valor de estado, enviamos 'Extranjero'
                    estadoSelect.setAttribute("name", config.estadoFieldName);
                    estadoSelect.innerHTML = `<option value="Extranjero" selected>Extranjero</option>`;
                } else {
                    estadoSelect.removeAttribute("name");
                }
                estadoSelect.required = false;
            }
            if (ciudadSelect) {
                ciudadSelect.style.display = "none";
                ciudadSelect.removeAttribute("name");
                ciudadSelect.required = false;
                ciudadSelect.value = "";
            }
            if (ciudadInput) {
                ciudadInput.style.display = "block";
                if (config.ciudadFieldName) {
                    ciudadInput.setAttribute("name", config.ciudadFieldName);
                }
                ciudadInput.required = true;
            }
            if (ciudadOtroContainer) {
                ciudadOtroContainer.style.display = "none";
                if (ciudadOtroInput) {
                    ciudadOtroInput.value = "";
                    ciudadOtroInput.removeAttribute("name");
                }
            }
        } else {
            // Vacío
            if (estadoContainer) estadoContainer.style.display = "none";
            if (ciudadContainer) ciudadContainer.style.display = "none";
        }

        updateConsolidated();
    }

    // 6. Manejador de cambio de Estado
    function onEstadoChange() {
        if (!estadoSelect) return;
        const est = estadoSelect.value;
        poblarCiudades(est);
        if (ciudadOtroContainer) {
            ciudadOtroContainer.style.display = "none";
            if (ciudadOtroInput) {
                ciudadOtroInput.value = "";
                ciudadOtroInput.removeAttribute("name");
                if (config.ciudadFieldName && ciudadSelect) {
                    ciudadSelect.setAttribute("name", config.ciudadFieldName);
                }
            }
        }
        updateConsolidated();
    }

    // 7. Manejador de cambio de Ciudad Select
    function onCiudadSelectChange() {
        if (!ciudadSelect) return;
        const val = ciudadSelect.value;
        const isOtro = val.startsWith("Otro ") || val.startsWith("Otra ");
        if (isOtro && ciudadOtroContainer) {
            ciudadOtroContainer.style.display = "block";
            if (ciudadOtroInput) {
                ciudadOtroInput.required = true;
                if (config.ciudadFieldName) {
                    ciudadSelect.removeAttribute("name");
                    ciudadOtroInput.setAttribute("name", config.ciudadFieldName);
                }
                ciudadOtroInput.focus();
            }
        } else if (ciudadOtroContainer) {
            ciudadOtroContainer.style.display = "none";
            if (ciudadOtroInput) {
                ciudadOtroInput.required = false;
                ciudadOtroInput.value = "";
                if (config.ciudadFieldName) {
                    ciudadOtroInput.removeAttribute("name");
                    ciudadSelect.setAttribute("name", config.ciudadFieldName);
                }
            }
        }
        updateConsolidated();
    }

    // Asignar listeners
    paisSelect.addEventListener("change", onPaisChange);
    if (estadoSelect) estadoSelect.addEventListener("change", onEstadoChange);
    if (ciudadSelect) ciudadSelect.addEventListener("change", onCiudadSelectChange);
    if (ciudadInput) ciudadInput.addEventListener("input", updateConsolidated);
    if (ciudadOtroInput) ciudadOtroInput.addEventListener("input", updateConsolidated);

    // Inicializar estado inicial
    onPaisChange();
    if (config.defaultEstado && estadoSelect) {
        estadoSelect.value = config.defaultEstado;
        poblarCiudades(config.defaultEstado);
        if (config.defaultCiudad && ciudadSelect) {
            ciudadSelect.value = config.defaultCiudad;
        }
    }
    updateConsolidated();
}
