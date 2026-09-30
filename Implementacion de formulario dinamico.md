como implemento un formulario dinamico donde elijo en una lista el campo "Pais" el pais de procedencia (mayoritariamente mexico), el formulario se actualiza en el campo "Estado" con todos los estados y al elegir estado se actualiza el campo "Ciudad" con las ciudades disponibles. En caso de elegir un pais que no sea Mexico que se actualize el formulario y solo tenga el campo ciudad como entrada de texto (no lista)

Para resolver esto de la forma más limpia y compatible con cualquier backend, la mejor estrategia es usar **HTML estándar y Vanilla JavaScript**. En lugar de crear y destruir elementos, mantendremos ambos campos de ciudad (la lista y la entrada de texto) en el HTML, y alternaremos su visibilidad y su atributo `name` dependiendo de la selección del país.

Aquí tienes la implementación completa:

HTML

```
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Formulario Dinámico</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 400px; margin: 20px auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        select, input[type="text"] { width: 100%; padding: 8px; box-sizing: border-box; }

        /* Clase clave para la lógica visual */
        .oculto { display: none; }
    </style>
</head>
<body>

    <form action="/tu-endpoint-backend" method="POST">

        <!-- 1. PAÍS -->
        <div class="form-group">
            <label for="pais">País de Procedencia</label>
            <select id="pais" name="pais" required>
                <option value="">Seleccione un país...</option>
                <option value="Mexico">México</option>
                <option value="Estados Unidos">Estados Unidos</option>
                <option value="Canada">Canadá</option>
                <option value="Colombia">Colombia</option>
            </select>
        </div>

        <!-- 2. ESTADO (Visible inicialmente solo si se elige México) -->
        <div class="form-group oculto" id="contenedorEstado">
            <label for="estado">Estado</label>
            <select id="estado" name="estado">
                <option value="">Seleccione un estado...</option>
                <!-- Opciones inyectadas por JS -->
            </select>
        </div>

        <!-- 3. CIUDAD -->
        <div class="form-group oculto" id="contenedorCiudad">
            <label for="ciudad">Ciudad</label>

            <!-- A: Select para cuando es México -->
            <select id="ciudadSelect" class="oculto">
                <option value="">Seleccione una ciudad...</option>
                <!-- Opciones inyectadas por JS -->
            </select>

            <!-- B: Input text para otros países -->
            <input type="text" id="ciudadInput" class="oculto" placeholder="Escriba su ciudad">
        </div>

        <button type="submit">Enviar</button>

    </form>

    <script>
        // Diccionario de datos (Idealmente esto viene de una API o Base de Datos)
        const datosMexico = {
            "Puebla": ["Puebla", "Cholula", "Santiago Miahuatlán", "Tehuacán", "Huaquechula"],
            "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque"],
            "Nuevo León": ["Monterrey", "San Pedro", "Guadalupe"]
        };

        // Referencias al DOM
        const paisSelect = document.getElementById('pais');

        const contenedorEstado = document.getElementById('contenedorEstado');
        const estadoSelect = document.getElementById('estado');

        const contenedorCiudad = document.getElementById('contenedorCiudad');
        const ciudadSelect = document.getElementById('ciudadSelect');
        const ciudadInput = document.getElementById('ciudadInput');

        // Lógica principal: Cambio de País
        paisSelect.addEventListener('change', function() {
            const pais = this.value;

            // Limpiar campos inferiores siempre que el país cambie
            estadoSelect.innerHTML = '<option value="">Seleccione un estado...</option>';
            ciudadSelect.innerHTML = '<option value="">Seleccione una ciudad...</option>';
            ciudadSelect.value = '';
            ciudadInput.value = '';

            if (pais === 'Mexico') {
                // Configurar para México
                contenedorEstado.classList.remove('oculto');
                contenedorCiudad.classList.remove('oculto');

                // Mostrar select de ciudad, ocultar input
                ciudadSelect.classList.remove('oculto');
                ciudadSelect.setAttribute('name', 'ciudad');

                ciudadInput.classList.add('oculto');
                ciudadInput.removeAttribute('name');

                // Llenar el select de Estados
                for (let estado in datosMexico) {
                    let option = document.createElement('option');
                    option.value = estado;
                    option.textContent = estado;
                    estadoSelect.appendChild(option);
                }

            } else if (pais !== '') {
                // Configurar para Extranjero
                contenedorEstado.classList.add('oculto');
                contenedorCiudad.classList.remove('oculto');

                // Ocultar select de ciudad, mostrar input
                ciudadSelect.classList.add('oculto');
                ciudadSelect.removeAttribute('name');

                ciudadInput.classList.remove('oculto');
                ciudadInput.setAttribute('name', 'ciudad'); // El input toma el control del form

            } else {
                // Reset (Ningún país seleccionado)
                contenedorEstado.classList.add('oculto');
                contenedorCiudad.classList.add('oculto');
            }
        });

        // Lógica secundaria: Cambio de Estado (Solo aplica para México)
        estadoSelect.addEventListener('change', function() {
            const estado = this.value;

            // Limpiar ciudades anteriores
            ciudadSelect.innerHTML = '<option value="">Seleccione una ciudad...</option>';

            if (estado && datosMexico[estado]) {
                // Llenar con las ciudades del estado seleccionado
                datosMexico[estado].forEach(function(ciudad) {
                    let option = document.createElement('option');
                    option.value = ciudad;
                    option.textContent = ciudad;
                    ciudadSelect.appendChild(option);
                });
            }
        });
    </script>
</body>
</html>
```

### Por qué esta estructura funciona tan bien:

1. **Gestión del atributo `name`:** Observa cómo JavaScript añade `setAttribute('name', 'ciudad')` al campo activo y se lo quita `removeAttribute('name')` al campo oculto. Esto asegura que cuando el formulario se envía al servidor, el backend siempre recibe exactamente una variable llamada `"ciudad"`, sin importar si el usuario usó la lista desplegable o el campo de texto.
2. **Performance del DOM:** Al usar `classList.add('oculto')`, evitas tener que destruir y recrear elementos HTML constantemente, lo cual reduce la posibilidad de pérdida de foco (focus loss) y mantiene tu código más predecible.
3. **Escalabilidad de datos:** La constante `datosMexico` actúa como un diccionario. En un entorno de producción, puedes reemplazar fácilmente ese bloque duro de código por una llamada `fetch()` a tu backend (o un endpoint REST) para cargar los estados y ciudades de forma asíncrona sin recargar la página.

Listado de Juntas Auxiliares

Las 10 comunidades que tienen el rango de junta auxiliar en Huaquechula son:

- Cacaloxúchitl

- Mártir Cuauhtémoc (antes referido en algunos registros o eventos locales)

- San Antonio Cuautla

- San Diego el Organal (San Diego Organal)

- San Juan Huiluco

- Santa Ana Coatepec

- Santiago Tetla

- Soledad Morelos

- Teacalco de Dorantes

- Tezonteopan de Bonilla (Tezoteopan de Bonilla)
