const editarImagen = document.getElementById("image");

editarImagen.addEventListener("change", cambiarImagen);

function toggleProfilePanel() {
    const panel = document.getElementById("profilePanel");
    panel.classList.toggle("show");
}

function editable(id) {
    const input = crearInputs(id);
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            guardarTexto(input);
        }
    });

    input.addEventListener("blur", function () {
        guardarTexto(input);
    });
}

function guardarTexto(input) {
    if (input.dataset.saved === "true") return;
    input.dataset.saved = "true";

    const value = input.value.trim();
    const id = input.id;
    const icon = document.getElementById(`icon-${id}`);
    const errorElem = document.getElementById(`${id}-error`);

    if (value === "") {
        errorElem.textContent = "Este campo no puede estar vacío.";
        input.focus();
        input.dataset.saved = "false"; // permitir reintento
        return;
    }

    if (id === "email" && !validarEmail(value)) {
        errorElem.textContent = "El email no es válido.";
        input.focus();
        input.dataset.saved = "false";
        return;
    }

    errorElem.remove();

    icon.classList.remove("fa-save");
    icon.classList.add("fa-pencil");

    const span = document.createElement("span");
    span.id = id;
    span.setAttribute("name", input.name);
    span.className = "editable-text me-2";
    span.textContent = value;
    input.replaceWith(span);
}

function cambiarImagen(event) {
    const imagenPerfil = document.getElementById("imagenPerfil");
    const archivo = event.target.files[0];
    if (archivo) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagenPerfil.src = e.target.result;
        };
        reader.readAsDataURL(archivo);
    }
}

function crearInputs(id){
    const span = document.getElementById(id);
    const icon = document.getElementById(`icon-${id}`);
    const currentText = span.textContent;

    const input = document.createElement("input");
    input.type = "text";
    input.value = currentText;
    input.className = "editable-text me-2";
    input.id = id;
    input.name = span.getAttribute("name")

    // Prevenir duplicados
    let error = document.getElementById(`${id}-error`);
    if (!error) {
        error = document.createElement("div");
        error.id = `${id}-error`;
        error.className = "text-danger-emphasis mt-1";
        error.style.fontSize = "0.9rem";
        span.parentNode.appendChild(error);
    } else {
        error.textContent = "";
    }

    icon.classList.remove("fa-pencil");
    icon.classList.add("fa-save");
    span.replaceWith(input);
    input.focus();
    return input;
}

function actualizarPerfil(){
    const formulario = document.getElementById("formulario-perfil");
    const username = crearInputs("username");
    if(username.value.trim() === ""){
        username.focus();
        return
    }
    const email = crearInputs("email");
    if(email.value.trim() === ""){
        email.focus();
        return
    }
    formulario.submit();
}

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function getListaEjercicios(){
    fetch(`/ejercicios/`)
      .then(response => response.json())
      .then(data => {
        const lista = document.querySelector('#historial-ejercicios > tbody');
        lista.innerHTML = '';  // Limpia lista anterior
        if (data.length === 0) {
          lista.innerHTML = '<tr><td>No hay ejercicios</td></tr>';
        } else {
          data.forEach(ejercicio => {
            const fila = document.createElement('tr');
            fila.classList.add('text-center');
            const tipo = document.createElement('td');
            const respuesta = document.createElement('td');
            const editar = document.createElement('td');
            const eliminar = document.createElement('td');

            respuesta.classList.add('math-display','respuesta-ecuacion');
            respuesta.textContent = `$$${ejercicio.respuesta}$$`;
            if( ejercicio.tipo === "hermite"){
                tipo.textContent = "H";
                eliminar.classList.add('p-0');
                editar.innerHTML = `<a href="/hermite/${ejercicio.id}/" class="btn btn-white rounded-pill fs-6 text-nowrap m-0">Editar <i class="fa fa-pencil"></i></a>`;
                eliminar.innerHTML = `<a href="/eliminar-hermite/${ejercicio.id}/" class="btn btn-danger rounded-pill fs-6 text-nowrap m-0">Eliminar <i class="fa fa-trash"></i></a>`;
            }
            else if(ejercicio.tipo === "integracion"){
                tipo.textContent = "I";
                editar.innerHTML = `<a href="/integracion/${ejercicio.id}/" class="btn btn-white rounded-pill fs-6 text-nowrap m-0">Editar <i class="fa fa-pencil"></i></a>`;
                eliminar.innerHTML = `<a href="/eliminar-integracion/${ejercicio.id}/" class="btn btn-danger rounded-pill fs-6 text-nowrap m-0">Eliminar <i class="fa fa-trash"></i></a>`;
            }
            fila.appendChild(tipo);
            fila.appendChild(respuesta);
            fila.appendChild(editar);
            fila.appendChild(eliminar);
            lista.appendChild(fila);

            MathJax.typeset();  // Renderiza las ecuaciones matemáticas
          });
        }
      });
}

getListaEjercicios();