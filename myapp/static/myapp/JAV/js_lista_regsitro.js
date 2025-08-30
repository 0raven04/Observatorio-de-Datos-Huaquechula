
// ===== ELIMINACIÓN INDIVIDUAL =====
// Añade evento click a todos los botones de eliminar
document.querySelectorAll('.btn-eliminar').forEach(button => {
    button.addEventListener('click', function () {
        // Obtiene el ID del registro a eliminar
        const id = this.getAttribute('data-id');

        // Solicita confirmación al usuario
        if (confirm(`¿Eliminar registro ${id}?`)) {
            // Redirige a la URL de eliminación
            window.location.href = `/visitas/eliminar/${id}/`;
        }
    });
});

// ===== EDICIÓN DE REGISTROS =====
// Añade evento click a todos los botones de editar
document.querySelectorAll('.btn-editar').forEach(button => {
    button.addEventListener('click', function () {
        // Obtiene el ID del registro a editar
        const id = this.getAttribute('data-id');

        // Prepara el formulario
        document.getElementById('formulario').reset();
        document.getElementById('camposPersonas').innerHTML = '';

        // Obtiene datos del registro via API
        fetch(`/visitas/obtener/${id}/`)
            .then(response => response.json())
            .then(data => {
                // Llena campos básicos
                document.getElementById('numPersonas').value = data.tamanio_grupo;
                document.getElementById('numDias').value = data.estancia_dias;
                document.getElementById('numVisitas').value = data.numero_visitas;
                document.getElementById('procedencia').value = data.procedencia || '';

                // Configura radio button para extranjero
                if (data.es_extranjero) {
                    document.getElementById('gridRadios1').checked = true;
                } else {
                    document.getElementById('gridRadios2').checked = true;
                }

                // Llena campos de selección
                document.getElementById('pais').value = data.pais_origen || '';
                document.getElementById('transporte').value = data.tipo_transporte || '';
                document.getElementById('motivo').value = data.motivo_visita || '';

                // Genera campos dinámicos de personas con datos
                generarCamposPersonas(data.tamanio_grupo, data.personas);

                // Cambia acción del formulario para edición
                document.getElementById('formulario').action = `/visitas/editar/${id}/`;

                // Muestra el modal
                const modal = new bootstrap.Modal(document.getElementById('miModal'));
                modal.show();
            });
    });
});

// ===== ELIMINACIÓN MÚLTIPLE =====
// Evento para el botón de eliminar selección
document.getElementById('botonEliminar').addEventListener('click', function () {
    // Obtiene checkboxes seleccionados
    const checkboxes = document.querySelectorAll('.checkbox-seleccion:checked');
    const ids = Array.from(checkboxes).map(cb => cb.value);

    // Valida que se haya seleccionado al menos un registro
    if (ids.length === 0) {
        alert('Seleccione al menos un registro');
        return;
    }

    // Solicita confirmación
    if (confirm(`¿Eliminar ${ids.length} registros seleccionados?`)) {
        // Construye URL con parámetros
        window.location.href = `/visitas/eliminar-seleccionados/?ids=${ids.join(',')}`;
    }
});

// ===== PREPARACIÓN DE NUEVO REGISTRO =====
// Evento para el botón de nuevo registro
document.getElementById('btnNuevoRegistro').addEventListener('click', function () {
    // Resetea el formulario
    document.getElementById('formulario').reset();

    // Restaura acción original para creación
    //document.getElementById('formulario').action = "{% url 'lista_registros' %}";
    document.getElementById('formulario').action = this.getAttribute('data-url');

    // Limpia campos dinámicos
    document.getElementById('camposPersonas').innerHTML = '';
});

// Script para manejo dinámico de campos de personas -->

/**
 * FUNCIÓN: generarCamposPersonas
 * Propósito: Genera campos de edad y género dinámicamente según el número de personas
 * Parámetros:
 *   num - Número de personas (entero)
 *   personasData - Datos opcionales para precargar (array de objetos)
 */
function generarCamposPersonas(num, personasData = []) {
    const container = document.getElementById('camposPersonas');
    container.innerHTML = '';

    for (let i = 1; i <= num; i++) {
        // Obtener datos para esta persona si existen
        const persona = personasData[i - 1] || {};

        // Plantilla HTML para cada persona
        container.innerHTML += `
                    <div class="row mb-3">
                        <div class="col-md-12">
                            <h5>Persona ${i}</h5>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating">
                                <!-- 
                                    Campo Edad:
                                    - name: edad1, edad2, ... 
                                    - value: Precarga datos si existen
                                    - Validación: min 1, max 120, requerido
                                -->
                                <input type="number" class="form-control" id="edad${i}" name="edad${i}" 
                                       placeholder="Edad" min="1" max="120" required 
                                       value="${persona.edad || ''}">
                                <label for="edad${i}">Edad</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating">
                                <!-- 
                                    Selector Género:
                                    - name: genero1, genero2, ...
                                    - Precarga selección usando atributo 'selected'
                                -->
                                <select class="form-select" id="genero${i}" name="genero${i}" required>
                                    <option value="">Selecciona género</option>
                                    <option value="Hombre" ${persona.sexo === 'Hombre' ? 'selected' : ''}>Hombre</option>
                                    <option value="Mujer" ${persona.sexo === 'Mujer' ? 'selected' : ''}>Mujer</option>
                                    <option value="Otro" ${persona.sexo === 'Otro' ? 'selected' : ''}>Otro</option>
                                </select>
                                <label for="genero${i}">Género</label>
                            </div>
                        </div>
                    </div>
                `;
    }
}

// EVENTO: Cambio en el campo número de personas
// Propósito: Genera campos dinámicos al cambiar el valor
document.getElementById('numPersonas').addEventListener('change', function () {
    const num = parseInt(this.value) || 0;
    generarCamposPersonas(num);
});

// EVENTO: Carga inicial del documento
// Propósito: Inicializar con campos vacíos
document.addEventListener('DOMContentLoaded', function () {
    const num = parseInt(document.getElementById('numPersonas').value) || 0;
    generarCamposPersonas(num);
});


const numInput = document.getElementById('numPersonas');
numInput.addEventListener("keypress", soloNumeros);
const container = document.getElementById('camposPersonas');
const pais= document.getElementById('pais');
const procedencia= document.getElementById('procedencia');
procedencia.addEventListener("keypress", soloLetras);
const transporte= document.getElementById('transporte');
const motivo= document.getElementById('motivo');
const numDias= document.getElementById('numDias');
numDias.addEventListener("keypress", soloNumeros);
const numVisitas= document.getElementById('numVisitas');
numVisitas.addEventListener("keypress", soloNumeros);



        (function() {
            'use strict'
            const forms = document.querySelectorAll('.needs-validation')
            
            Array.from(forms).forEach(form => {
              form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                  event.preventDefault()
                  event.stopPropagation()
                }
                
                form.classList.add('was-validated')
              }, false)
            })
          })()


document.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", function() {
        this.classList.remove("is-valid");
        this.classList.remove("is-invalid");
    });
});

function soloLetras(event) {
    let caja = event.target;
    caja.value = caja.value.replace(/[^a-zA-ZáÁéÉíÍóÓúÚ\s]/g, "");
}

function soloNumeros(event) {
    let caja = event.target;
    caja.value = caja.value.replace(/[^0-9]/g, "");
}














