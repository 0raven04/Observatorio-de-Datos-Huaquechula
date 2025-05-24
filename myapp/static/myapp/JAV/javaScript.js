const numInput = document.getElementById('numPersonas');
numInput.addEventListener("keypress", soloNumeros);
const container = document.getElementById('personasContainer');
const pais= document.getElementById('pais');
const procedencia= document.getElementById('procedencia');
procedencia.addEventListener("keypress", soloLetras);
const transporte= document.getElementById('transporte');
const motivo= document.getElementById('motivo');
const numDias= document.getElementById('numDias');
numDias.addEventListener("keypress", soloNumeros);
const numVisitas= document.getElementById('numVisitas');
numVisitas.addEventListener("keypress", soloNumeros);
      
        function crearCamposPersonas(cantidad) {
          container.innerHTML = ''; // Limpiar campos anteriores
      
          for (let i = 1; i <= cantidad; i++) {
            const div = document.createElement('div');
            div.classList.add('mb-3');
            div.innerHTML = `

               <div class="row mt-5">
                <p class="h5 text-center mb-3">Persona ${i}</p>
                <div class="mt-3 col-12 col-sm-6 col-md-6 mb-3 mb-md-0 d-flex flex-column align-items-center text-center"> 
                    <label for="edad${i}" class="form-label">Edad</label>
                    <input type="number" class="form-control mb-2" id="edad${i}" name="edad${i}" min="0" max="115" required>
                    <div class="invalid-feedback">
                      Ingresa una edad válida
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-md-6 mb-3 mb-md-0 d-flex flex-column align-items-center text-center mt-3 !important">
                    <label for="genero${i}" class="form-label">Género</label>
                    <select class="form-select" id="genero${i}" name="genero${i}" required>
                    <option value="" disabled selected>Selecciona género</option>
                    <option value="Hombre">Hombre</option>
                    <option value="Mujer">Mujer</option>
                    <option value="Otro">Otro</option>
                    </select>
                    <div class="invalid-feedback">
                      Selecciona una opción
                    </div>
                </div>
                </div>
                <hr class="my-3 d-md-none">
            `;
            container.appendChild(div);
          }
        }
      
        numInput.addEventListener('input', () => {
          const cantidad = parseInt(numInput.value);
          if (!isNaN(cantidad) && cantidad > 0) {
            crearCamposPersonas(cantidad);
          } else {
            container.innerHTML = '';
          }
        });
      

        document.addEventListener('DOMContentLoaded', () => {
          crearCamposPersonas(parseInt(numInput.value));
        });

        (function() {
            'use strict'
            
            const forms = document.querySelectorAll('.needs-validation')
            
            Array.from(forms).forEach(form => {
              form.addEventListener('submit', event => {
                //if (!form.checkValidity()) {
                  //event.preventDefault()
                  //event.stopPropagation()
                //}
                
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


document.addEventListener('DOMContentLoaded', () => {
  const radioSi = document.getElementById("gridRadios1");
  const radioNo = document.getElementById("gridRadios2");

  const campoPais = document.getElementById("pais");
  const contenedorPais = campoPais.closest(".col-12");

  function actualizarCampoPais() {
    const mostrarPais = radioSi.checked;

    campoPais.disabled = !mostrarPais;

    if (!mostrarPais) {
      campoPais.value = "";
      contenedorPais.classList.add("d-none");
    } else {
      contenedorPais.classList.remove("d-none");
    }
  }


  actualizarCampoPais();

  radioSi.addEventListener("change", actualizarCampoPais);
  radioNo.addEventListener("change", actualizarCampoPais);
});

document.addEventListener('DOMContentLoaded', () => {
  crearCamposPersonas(parseInt(document.getElementById('numPersonas').value || 1));
});




