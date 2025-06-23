// Manejo de puntos de Hermite con tabla interactiva
let contadorPuntos = 0
const Swal = window.Swal // Declare the Swal variable

document.addEventListener("DOMContentLoaded", () => {
  inicializarTablaPuntos()

  // Manejar envío del formulario
  const form = document.getElementById("hermiteForm")
  if (form) {
    form.addEventListener("submit", (e) => {
      if (!validarYActualizarPuntos()) {
        e.preventDefault()
        return false
      }
    })
  }
})

function inicializarTablaPuntos() {
  // Cargar puntos existentes si los hay (para cuando se recarga la página con errores)
  const puntosInput = document.querySelector('input[name="puntos"]')
  if (puntosInput && puntosInput.value) {
    cargarPuntosDesdeString(puntosInput.value)
  } else {
    // Agregar 2 puntos por defecto
    agregarPunto(0, 1, 2)
    agregarPunto(1, 4, 5)
  }
}

function agregarPunto(x = "", fx = "", dfx = "") {
  const tbody = document.getElementById("puntos-tbody")
  const fila = document.createElement("tr")
  fila.setAttribute("data-punto-id", contadorPuntos)

  fila.innerHTML = `
        <td class="text-center align-middle">
            <strong>P${contadorPuntos + 1}</strong>
        </td>
        <td>
            <input type="number" 
                   class="form-control form-control-sm x-input" 
                   value="${x}" 
                   step="any" 
                   data-index="${contadorPuntos}" 
                   style="background:#e3f2fd; border:1px solid #90caf9;"
                   placeholder="0"
                   required>
        </td>
        <td>
            <input type="number" 
                   class="form-control form-control-sm fx-input" 
                   value="${fx}" 
                   step="any" 
                   data-index="${contadorPuntos}" 
                   style="background:#e8f5e9; border:1px solid #a5d6a7;"
                   placeholder="f(x)"
                   required>
        </td>
        <td>
            <input type="number" 
                   class="form-control form-control-sm derivada-input" 
                   value="${dfx}" 
                   step="any" 
                   data-index="${contadorPuntos}" 
                   style="background:#fff3e0; border:1px solid #ffcc80;"
                   placeholder="f'(x)"
                   required>
        </td>
        <td class="text-center align-middle">
            <button type="button" 
                    class="btn btn-outline-danger btn-sm" 
                    onclick="eliminarPunto(this)"
                    title="Eliminar punto">
                <i class="fas fa-times"></i>
            </button>
        </td>
    `

  tbody.appendChild(fila)
  contadorPuntos++

  // Actualizar numeración
  actualizarNumeracionPuntos()

  // Agregar event listeners para validación en tiempo real
  agregarValidacionTiempoReal(fila)
}

function eliminarPunto(boton) {
  const fila = boton.closest("tr")
  const tbody = document.getElementById("puntos-tbody")

  // No permitir eliminar si solo quedan 2 puntos
  if (tbody.children.length <= 2) {
    Swal.fire({
      title: "Mínimo requerido",
      text: "Se necesitan al menos 2 puntos para la interpolación de Hermite.",
      icon: "warning",
      confirmButtonColor: "#ffc107",
      customClass: { popup: "swal2-modal-custom" },
    })
    return
  }

  // Confirmar eliminación
  Swal.fire({
    title: "¿Eliminar punto?",
    text: "¿Estás seguro de que quieres eliminar este punto?",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-trash"></i> Eliminar',
    cancelButtonText: '<i class="fas fa-times"></i> Cancelar',
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
    customClass: { popup: "swal2-modal-custom" },
  }).then((result) => {
    if (result.isConfirmed) {
      fila.remove()
      actualizarNumeracionPuntos()

      Swal.fire({
        title: "Eliminado",
        text: "El punto ha sido eliminado.",
        icon: "success",
        timer: 1500,
        showConfirmButton: false,
        customClass: { popup: "swal2-modal-custom" },
      })
    }
  })
}

function actualizarNumeracionPuntos() {
  const filas = document.querySelectorAll("#puntos-tbody tr")
  filas.forEach((fila, index) => {
    const celda = fila.querySelector("td:first-child strong")
    if (celda) {
      celda.textContent = `P${index + 1}`
    }

    // Actualizar data-index de los inputs
    const inputs = fila.querySelectorAll("input")
    inputs.forEach((input) => {
      input.setAttribute("data-index", index)
    })
  })
}

function agregarValidacionTiempoReal(fila) {
  const inputs = fila.querySelectorAll('input[type="number"]')

  inputs.forEach((input) => {
    input.addEventListener("input", function () {
      validarInput(this)
    })

    input.addEventListener("blur", () => {
      validarPuntosUnicos()
    })
  })
}

function validarInput(input) {
  const valor = input.value.trim()

  if (valor === "") {
    input.classList.remove("is-valid", "is-invalid")
    return
  }

  const numero = Number.parseFloat(valor)
  if (isNaN(numero)) {
    input.classList.add("is-invalid")
    input.classList.remove("is-valid")
    input.title = "Debe ser un número válido"
  } else {
    input.classList.add("is-valid")
    input.classList.remove("is-invalid")
    input.title = ""
  }
}

function validarPuntosUnicos() {
  const xInputs = document.querySelectorAll(".x-input")
  const valores = []
  let hayDuplicados = false

  // Limpiar clases previas
  xInputs.forEach((input) => {
    input.classList.remove("is-invalid")
    input.title = ""
  })

  // Verificar duplicados
  xInputs.forEach((input) => {
    const valor = Number.parseFloat(input.value)
    if (!isNaN(valor)) {
      if (valores.includes(valor)) {
        input.classList.add("is-invalid")
        input.title = "Los valores de x deben ser únicos"
        hayDuplicados = true
      } else {
        valores.push(valor)
      }
    }
  })

  if (hayDuplicados) {
    mostrarAlerta("Los valores de x deben ser únicos para cada punto.", "warning")
  }

  return !hayDuplicados
}

function validarYActualizarPuntos() {
  const filas = document.querySelectorAll("#puntos-tbody tr")
  const puntos = []
  let valido = true

  // Validar que hay al menos 2 puntos
  if (filas.length < 2) {
    mostrarAlerta("Se necesitan al menos 2 puntos para la interpolación.", "error")
    return false
  }

  // Validar cada punto
  filas.forEach((fila, index) => {
    const xInput = fila.querySelector(".x-input")
    const fxInput = fila.querySelector(".fx-input")
    const derivadaInput = fila.querySelector(".derivada-input")

    const x = Number.parseFloat(xInput.value)
    const fx = Number.parseFloat(fxInput.value)
    const dfx = Number.parseFloat(derivadaInput.value)

    if (isNaN(x) || isNaN(fx) || isNaN(dfx)) {
      mostrarAlerta(`El punto P${index + 1} tiene valores inválidos.`, "error")
      valido = false
      return
    }

    puntos.push([x, fx, dfx])
  })

  if (!valido) return false

  // Validar que no hay x duplicados
  const xValues = puntos.map((p) => p[0])
  const uniqueX = new Set(xValues)
  if (uniqueX.size !== xValues.length) {
    mostrarAlerta("Los valores de x deben ser únicos.", "error")
    return false
  }

  // Actualizar campo oculto
  const puntosString = puntos.map((p) => `${p[0]},${p[1]},${p[2]}`).join(";")
  document.getElementById("puntos-hidden").value = puntosString

  return true
}

function cargarPuntosDesdeString(puntosString) {
  if (!puntosString) return

  // Limpiar tabla
  document.getElementById("puntos-tbody").innerHTML = ""
  contadorPuntos = 0

  // Cargar puntos
  const puntos = puntosString.split(";")
  puntos.forEach((puntoStr) => {
    if (puntoStr.trim()) {
      const [x, fx, dfx] = puntoStr.split(",").map((v) => Number.parseFloat(v.trim()))
      if (!isNaN(x) && !isNaN(fx) && !isNaN(dfx)) {
        agregarPunto(x, fx, dfx)
      }
    }
  })

  // Si no se cargó ningún punto, agregar los por defecto
  if (contadorPuntos === 0) {
    agregarPunto(0, 1, 2)
    agregarPunto(1, 4, 5)
  }
}

function cargarEjemplo() {
  Swal.fire({
    title: "Cargar ejemplo",
    text: "¿Quieres cargar un ejemplo predefinido? Esto reemplazará los puntos actuales.",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-lightbulb"></i> Cargar ejemplo',
    cancelButtonText: '<i class="fas fa-times"></i> Cancelar',
    confirmButtonColor: "#ffc107",
    cancelButtonColor: "#6c757d",
    customClass: { popup: "swal2-modal-custom" },
  }).then((result) => {
    if (result.isConfirmed) {
      // Limpiar tabla
      document.getElementById("puntos-tbody").innerHTML = ""
      contadorPuntos = 0

      // Cargar ejemplo: f(x) = x² + 1, f'(x) = 2x
      agregarPunto(0, 1, 0) // f(0) = 1, f'(0) = 0
      agregarPunto(1, 2, 2) // f(1) = 2, f'(1) = 2
      agregarPunto(2, 5, 4) // f(2) = 5, f'(2) = 4

      // Actualizar punto de evaluación
      document.getElementById("x_eval").value = 0.5

      Swal.fire({
        title: "Ejemplo cargado",
        text: "Se ha cargado un ejemplo basado en f(x) = x² + 1",
        icon: "success",
        timer: 2000,
        showConfirmButton: false,
        customClass: { popup: "swal2-modal-custom" },
      })
    }
  })
}

function mostrarAlerta(mensaje, tipo) {
  const iconos = {
    error: "error",
    warning: "warning",
    success: "success",
    info: "info",
  }

  Swal.fire({
    title: tipo === "error" ? "Error" : tipo === "warning" ? "Advertencia" : "Información",
    text: mensaje,
    icon: iconos[tipo] || "info",
    confirmButtonColor: tipo === "error" ? "#dc3545" : tipo === "warning" ? "#ffc107" : "#007bff",
    customClass: { popup: "swal2-modal-custom" },
  })
}

// Exportar funciones para uso global
window.agregarPunto = agregarPunto
window.eliminarPunto = eliminarPunto
window.cargarEjemplo = cargarEjemplo
