// ===== ARCHIVO JAVASCRIPT UNIFICADO PARA FORMULARIOS DE VISITAS =====
// Este archivo combina todas las funcionalidades de los scripts anteriores

document.addEventListener("DOMContentLoaded", function () {
    // ===== CONFIGURACIÓN INICIAL =====
    inicializarComponentes();
    
    // ===== MANEJO DE LISTAS DE REGISTROS (Botones editar/eliminar) =====
    inicializarManejoRegistros();
    
    // ===== FUNCIONES DE INICIALIZACIÓN =====
    function inicializarComponentes() {
        // 1. Manejo de totales y distribución por edad/género
        if (document.querySelector('.age-input') || document.querySelector('[name*="mujeres_"]')) {
            inicializarCalculoTotales();
        }
        
        // 2. Manejo de campos de extranjero
        if (document.querySelector('[name="es_extranjero"]') || document.querySelector('[name="gridRadios"]')) {
            inicializarExtranjeroToggle();
        }
        
        // 3. Configurar valores por defecto
        setDefaultValues();
        
        // 4. Manejo de validaciones de entrada
        inicializarValidacionesEntrada();
        
        // 5. Manejo de selección múltiple en listas
        if (document.getElementById('selectAll')) {
            inicializarSeleccionMultiple();
        }
        
        // 6. Validación de formularios Bootstrap
        inicializarValidacionBootstrap();
    }

    function inicializarManejoRegistros() {
        // ===== BOTONES DE EDICIÓN =====
        document.querySelectorAll('.btn-editar').forEach(button => {
            button.addEventListener('click', function() {
                const registroId = this.getAttribute('data-id');
                const url = this.getAttribute('data-url');
                
                // Cargar datos del registro
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        // Llenar el formulario modal con los datos
                        const tituloModal = document.getElementById('tituloModal');
                        if (tituloModal) {
                            tituloModal.textContent = 'Editar Registro #' + data.id_registro;
                        }
                        
                        // Llenar campos básicos
                        const estanciaDias = document.getElementById('estancia_dias');
                        const visitasPrevias = document.getElementById('visitas_previas');
                        const motivoVisita = document.getElementById('motivo_visita');
                        const tipoTransporte = document.getElementById('tipo_transporte');
                        const procedencia = document.getElementById('procedencia');
                        
                        if (estanciaDias) estanciaDias.value = data.estancia_dias || 1;
                        if (visitasPrevias) visitasPrevias.value = data.visitas_previas || 1;
                        if (motivoVisita) motivoVisita.value = data.motivo_visita || 'turismo';
                        if (tipoTransporte) tipoTransporte.value = data.tipo_transporte || 'automovil';
                        if (procedencia) procedencia.value = data.procedencia || '';
                        
                        // Campos de extranjero
                        const extranjeroSi = document.getElementById('extranjero_si');
                        const extranjeroNo = document.getElementById('extranjero_no');
                        const paisSelector = document.getElementById('paisSelector');
                        const paisOrigen = document.getElementById('pais_origen');
                        
                        if (data.es_extranjero) {
                            if (extranjeroSi) extranjeroSi.checked = true;
                            if (paisSelector) paisSelector.style.display = 'block';
                            if (paisOrigen) paisOrigen.value = data.pais_origen || 'Mexico';
                        } else {
                            if (extranjeroNo) extranjeroNo.checked = true;
                            if (paisSelector) paisSelector.style.display = 'none';
                            if (paisOrigen) paisOrigen.value = 'Mexico';
                        }
                        
                        // Campos de distribución por edad y género
                        const ageFields = [
                            'mujeres_0_15', 'mujeres_16_30', 'mujeres_31_45', 'mujeres_46_60', 'mujeres_61_75', 'mujeres_76_mas',
                            'hombres_0_15', 'hombres_16_30', 'hombres_31_45', 'hombres_46_60', 'hombres_61_75', 'hombres_76_mas'
                        ];
                        
                        ageFields.forEach(fieldName => {
                            const field = document.querySelector(`input[name="${fieldName}"]`);
                            if (field) {
                                field.value = data[fieldName] || 0;
                            }
                        });
                        
                        // Actualizar totales
                        if (typeof updateTotals === 'function') {
                            updateTotals();
                        }
                        
                        // Cambiar acción del formulario para edición
                        const form = document.getElementById('formulario');
                        if (form) {
                            // Si hay una URL específica para edición, usarla
                            const editUrl = this.getAttribute('data-edit-url');
                            if (editUrl) {
                                form.action = editUrl.replace('0', data.id_registro);
                            } else {
                                // Si no, usar el patrón genérico
                                form.action = `/visitas/editar/${data.id_registro}/`;
                            }
                        }
                        
                        // Mostrar modal si existe
                        const modalElement = document.getElementById('miModal');
                        if (modalElement && typeof bootstrap !== 'undefined') {
                            const modal = new bootstrap.Modal(modalElement);
                            modal.show();
                        }
                    })
                    .catch(error => {
                        console.error('Error al cargar datos:', error);
                        alert('Error al cargar los datos del registro');
                    });
            });
        });
        
        // ===== BOTONES DE ELIMINACIÓN INDIVIDUAL =====
        document.querySelectorAll('.btn-eliminar').forEach(button => {
            button.addEventListener('click', function() {
                const registroId = this.getAttribute('data-id');
                
                if (confirm('¿Está seguro de que desea eliminar este registro?')) {
                    // Si hay una URL específica para eliminación, usarla
                    const deleteUrl = this.getAttribute('data-delete-url');
                    if (deleteUrl) {
                        window.location.href = deleteUrl.replace('0', registroId);
                    } else {
                        // Si no, usar el patrón genérico
                        window.location.href = `/visitas/eliminar/${registroId}/`;
                    }
                }
            });
        });
        
        // ===== BOTÓN PARA ELIMINAR SELECCIÓN MÚLTIPLE =====
        const botonEliminarMultiple = document.getElementById('botonEliminar');
        if (botonEliminarMultiple) {
            botonEliminarMultiple.addEventListener('click', function() {
                const checkboxes = document.querySelectorAll('.checkbox-seleccion:checked');
                
                if (checkboxes.length === 0) {
                    alert('Por favor, seleccione al menos un registro para eliminar.');
                    return;
                }
                
                if (confirm(`¿Está seguro de que desea eliminar ${checkboxes.length} registro(s)?`)) {
                    const ids = Array.from(checkboxes).map(cb => cb.value).join(',');
                    window.location.href = `/visitas/eliminar-seleccionados/?ids=${ids}`;
                }
            });
        }
    }

    // ===== CÁLCULO DE TOTALES Y DISTRIBUCIÓN =====
    function inicializarCalculoTotales() {
        const ageInputs = document.querySelectorAll(".age-input, input[name*='mujeres_'], input[name*='hombres_']");
        const displayTotal = document.getElementById("display-total");
        const totalMujeresSpan = document.getElementById("total-mujeres");
        const totalHombresSpan = document.getElementById("total-hombres");
        const totalPersonasSpan = document.getElementById("total-personas");
        const totalPersonasHidden = document.getElementById("total-personas-hidden");

        // Función para actualizar los totales
        function updateTotals() {
            let totalMujeres = 0;
            let totalHombres = 0;
            let totalGeneral = 0;

            // Dos métodos posibles para calcular totales:
            // 1. Usando estructura con data attributes (nuevo formato)
            const gruposData = document.querySelectorAll('[data-group]');
            if (gruposData.length > 0) {
                const groups = ["0_15", "16_30", "31_45", "46_60", "61_75", "76_mas"];
                groups.forEach((group) => {
                    const mujeresInput = document.querySelector(
                        `input[data-group="${group}"][data-gender="mujeres"], [name="mujeres_${group}"]`
                    );
                    const hombresInput = document.querySelector(
                        `input[data-group="${group}"][data-gender="hombres"], [name="hombres_${group}"]`
                    );
                    
                    const mujeres = parseInt(mujeresInput?.value) || 0;
                    const hombres = parseInt(hombresInput?.value) || 0;
                    const groupTotal = mujeres + hombres;

                    // Actualizar total del grupo si existe el elemento
                    const groupTotalElement = document.querySelector(
                        `.group-total[data-group="${group}"]`
                    );
                    if (groupTotalElement) {
                        groupTotalElement.textContent = groupTotal;
                    }

                    totalMujeres += mujeres;
                    totalHombres += hombres;
                    totalGeneral += groupTotal;
                });
            } else {
                // 2. Usando estructura con nombres de campos (formato antiguo)
                const camposEdadGenero = document.querySelectorAll('input[name*="mujeres_"], input[name*="hombres_"]');
                camposEdadGenero.forEach(function(campo) {
                    const valor = parseInt(campo.value) || 0;
                    if (campo.name.includes('mujeres_')) {
                        totalMujeres += valor;
                    } else if (campo.name.includes('hombres_')) {
                        totalHombres += valor;
                    }
                });
                totalGeneral = totalMujeres + totalHombres;
            }

            // Actualizar totales generales
            if (totalMujeresSpan) totalMujeresSpan.textContent = totalMujeres;
            if (totalHombresSpan) totalHombresSpan.textContent = totalHombres;
            if (totalPersonasSpan) totalPersonasSpan.textContent = totalGeneral;
            if (displayTotal) displayTotal.textContent = totalGeneral;
            if (totalPersonasHidden) totalPersonasHidden.value = totalGeneral;
            
            return totalGeneral;
        }

        // Añadir event listeners a todos los inputs de edad
        ageInputs.forEach((input) => {
            input.addEventListener("input", function() {
                // Validar que no exceda 255
                let value = parseInt(this.value);
                if (isNaN(value)) value = 0;
                if (value > 255) {
                    this.value = 255;
                }
                if (value < 0) {
                    this.value = 0;
                }
                updateTotals();
            });
            input.addEventListener("change", updateTotals);
        });

        // Inicializar los totales
        updateTotals();
        
        // Exportar función para uso externo
        window.updateTotals = updateTotals;
    }

    // ===== TOGGLE PARA EXTRANJERO =====
    function inicializarExtranjeroToggle() {
        const esExtranjeroRadios = document.querySelectorAll('input[name="es_extranjero"], input[name="gridRadios"]');
        const paisSelector = document.getElementById("paisSelector") || document.getElementById("pais-origen-group");
        const paisOrigenSelect = document.getElementById("pais_origen") || document.getElementById("pais");
        const paisOrigenField = document.querySelector('[name="pais_origen"]');

        function togglePaisOrigen() {
            const esExtranjero = document.querySelector('input[name="es_extranjero"]:checked, input[name="gridRadios"]:checked');
            
            if (paisSelector) {
                if (esExtranjero && (esExtranjero.value === "1" || esExtranjero.value === "si")) {
                    paisSelector.style.display = "block";
                    if (paisSelector.classList) paisSelector.classList.remove("d-none");
                    if (paisOrigenSelect) paisOrigenSelect.setAttribute("required", "required");
                    if (paisOrigenField) paisOrigenField.required = true;
                } else {
                    paisSelector.style.display = "none";
                    if (paisSelector.classList) paisSelector.classList.add("d-none");
                    if (paisOrigenSelect) {
                        paisOrigenSelect.removeAttribute("required");
                        paisOrigenSelect.value = "Mexico"; // Establecer México por defecto
                    }
                    if (paisOrigenField) {
                        paisOrigenField.required = false;
                        paisOrigenField.value = "Mexico";
                    }
                }
            }
        }

        // Añadir event listeners
        esExtranjeroRadios.forEach(radio => {
            radio.addEventListener("change", togglePaisOrigen);
        });

        // Estado inicial
        togglePaisOrigen();
    }

    // ===== VALORES POR DEFECTO =====
    function setDefaultValues() {
        const paisOrigenSelect = document.getElementById("pais_origen") || document.getElementById("pais");
        const motivoVisitaSelect = document.getElementById("motivo_visita") || document.getElementById("motivo");
        const tipoTransporteSelect = document.getElementById("tipo_transporte") || document.getElementById("transporte");
        const numDiasInput = document.getElementById("estancia_dias") || document.getElementById("numDias");
        const numVisitasInput = document.getElementById("visitas_previas") || document.getElementById("numVisitas");

        // Establecer México como país por defecto
        if (paisOrigenSelect) {
            paisOrigenSelect.value = "Mexico";
        }

        // Establecer valores por defecto si no están configurados
        if (motivoVisitaSelect && !motivoVisitaSelect.value) {
            motivoVisitaSelect.value = "turismo";
        }

        if (tipoTransporteSelect && !tipoTransporteSelect.value) {
            tipoTransporteSelect.value = "automovil";
        }

        if (numDiasInput && !numDiasInput.value) {
            numDiasInput.value = "1";
        }

        if (numVisitasInput && !numVisitasInput.value) {
            numVisitasInput.value = "1";
        }
    }

    // ===== VALIDACIONES DE ENTRADA =====
    function inicializarValidacionesEntrada() {
        // Restricción para solo letras
        const camposLetras = document.querySelectorAll('#procedencia, [name="procedencia"]');
        camposLetras.forEach(campo => {
            campo.addEventListener("input", function() {
                this.value = this.value.replace(/[^a-zA-ZáÁéÉíÍóÓúÚñÑ\s]/g, "");
            });
        });

        // Restricción para solo números
        const camposNumeros = document.querySelectorAll('input[type="number"], #numPersonas, #numDias, #numVisitas, #estancia_dias, #visitas_previas');
        camposNumeros.forEach(campo => {
            campo.addEventListener("input", function() {
                this.value = this.value.replace(/[^0-9]/g, "");
                // Validar rango 0-255
                let value = parseInt(this.value);
                if (isNaN(value)) value = 0;
                if (value > 255) this.value = 255;
                if (value < 0) this.value = 0;
            });
        });
    }

    // ===== VALIDACIÓN BOOTSTRAP =====
    function inicializarValidacionBootstrap() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
                
                // Validación personalizada adicional
                if (!validarFormularioPersonalizado(form)) {
                    event.preventDefault();
                    event.stopPropagation();
                }
            }, false);
        });

        // Limpiar clases de validación al typing
        document.querySelectorAll("input, select").forEach(input => {
            input.addEventListener("input", function() {
                this.classList.remove("is-valid", "is-invalid");
            });
        });
    }

    function validarFormularioPersonalizado(form) {
        // Solo aplicar esta validación al formulario de registro de visitas o edición
        if (form.id !== 'formulario') {
            return true;
        }

        const totalPersonasElement = document.getElementById('total-personas') || document.getElementById('display-total');
        const totalGeneral = totalPersonasElement ? parseInt(totalPersonasElement.textContent) || 0 : 0;
        const esExtranjero = document.querySelector('input[name="es_extranjero"]:checked, input[name="gridRadios"]:checked');
        const paisOrigenField = document.getElementById("pais_origen") || document.getElementById("pais") || document.querySelector('[name="pais_origen"]');
        const paisOrigen = paisOrigenField ? paisOrigenField.value : '';
        const procedenciaField = document.getElementById("procedencia") || document.querySelector('[name="procedencia"]');
        const procedencia = procedenciaField ? procedenciaField.value.trim() : '';

        // Validar que haya al menos una persona
        if (totalGeneral < 1) {
            alert("Debe ingresar al menos una persona para registrar.");
            return false;
        }

        // Validar procedencia
        if (!procedencia || procedencia === "") {
            alert("Debe ingresar la procedencia.");
            return false;
        }

        // Si es extranjero, validar que se seleccione un país diferente a México
        if (esExtranjero && (esExtranjero.value === "1" || esExtranjero.value === "si")) {
            if (!paisOrigen || paisOrigen === "") {
                alert("Si el visitante es extranjero, debe seleccionar un país de origen.");
                return false;
            }
            if (paisOrigen === "Mexico") {
                if (!confirm("¿Está seguro que es extranjero pero seleccionó México como país de origen?")) {
                    return false;
                }
            }
        } else {
            // Si no es extranjero, establecer México como país
            if (paisOrigenField) {
                paisOrigenField.value = "Mexico";
            }
        }

        // Validar números dentro del rango
        const numberInputs = form.querySelectorAll('input[type="number"]');
        for (let input of numberInputs) {
            const value = parseInt(input.value);
            if (isNaN(value) || value < 0 || value > 255) {
                alert(`El valor en ${input.previousElementSibling?.textContent || input.name} debe estar entre 0 y 255.`);
                return false;
            }
        }

        return true;
    }

    // ===== SELECCIÓN MÚLTIPLE =====
    function inicializarSeleccionMultiple() {
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('.checkbox-seleccion');
                checkboxes.forEach(cb => cb.checked = this.checked);
            });
        }
    }
});

// ===== FUNCIONES GLOBALES PARA MANEJO DE REGISTROS =====
// Estas funciones pueden ser llamadas desde cualquier lugar

// Función para preparar nuevo registro
function prepararNuevoRegistro() {
    const form = document.getElementById('formulario');
    if (form) {
        form.reset();
        
        const btnNuevo = document.getElementById('btnNuevoRegistro');
        if (btnNuevo) {
            form.action = btnNuevo.getAttribute('data-url');
        }
        
        const tituloModal = document.getElementById('tituloModal');
        if (tituloModal) {
            tituloModal.textContent = 'Nuevo Registro';
        }
        
        const camposPersonas = document.getElementById('camposPersonas');
        if (camposPersonas) {
            camposPersonas.innerHTML = '';
        }
        
        // Reiniciar totales
        if (typeof window.updateTotals === 'function') {
            window.updateTotals();
        }
        
        // Ocultar selector de país
        const paisSelector = document.getElementById('paisSelector');
        if (paisSelector) {
            paisSelector.style.display = 'none';
        }
        
        // Establecer "No" en extranjero
        const extranjeroNo = document.getElementById('extranjero_no') || document.querySelector('input[name="es_extranjero"][value="0"]');
        if (extranjeroNo) {
            extranjeroNo.checked = true;
        }
    }
}

// Asignar evento al botón de nuevo registro si existe
document.getElementById('btnNuevoRegistro')?.addEventListener('click', prepararNuevoRegistro);

// ===== FUNCIONES AUXILIARES =====
function soloLetras(event) {
    let caja = event.target;
    caja.value = caja.value.replace(/[^a-zA-ZáÁéÉíÍóÓúÚ\s]/g, "");
}

function soloNumeros(event) {
    let caja = event.target;
    caja.value = caja.value.replace(/[^0-9]/g, "");
}