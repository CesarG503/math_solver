// Variables globales
let contadorRestricciones = 0
let numVariables = 2
let nombresVariables = ["x", "x"]

// Función para alternar tema
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme")
  const newTheme = currentTheme === "dark" ? "light" : "dark"
  document.documentElement.setAttribute("data-theme", newTheme)
  localStorage.setItem("theme", newTheme)
  updateThemeButton(newTheme)
  updateValorOptimoTheme(newTheme)
}

// Cambia la clase del texto de valor óptimo según el tema
function updateValorOptimoTheme(theme) {
  const valorOptimo = document.getElementById("valor-optimo")
  if (valorOptimo) {
    valorOptimo.classList.remove("text-warning", "text-warning-neon")
    if (theme === "dark") {
      valorOptimo.classList.add("text-warning-neon")
    } else {
      valorOptimo.classList.add("text-warning")
    }
  }
}

// Modificar updateThemeButton para actualizar el valor óptimo y la gráfica
function updateThemeButton(theme) {
  const icon = document.getElementById("theme-icon")
  const boton = document.querySelector(".theme-toggle")
  const body = document.body

  if (theme === "dark") {
    if (icon) icon.className = "fas fa-sun"
    if (boton) {
      boton.classList.remove("bg-secondary-neon")
      boton.classList.add("bg-warning-neon")
    }
    body.classList.add("bg-dark")
    body.classList.add("text-light")
  } else {
    if (icon) icon.className = "fas fa-moon"
    if (boton) {
      boton.classList.remove("bg-warning-neon")
      boton.classList.add("bg-secondary-neon")
    }
    body.classList.remove("bg-dark")
    body.classList.remove("text-light")
  }
  updateValorOptimoTheme(theme)

  // Actualizar tema de la gráfica de Simplex si existe
  if (typeof window.updateSimplexGraphTheme === "function") {
    window.updateSimplexGraphTheme(theme === "dark")
  }
}

// Cargar tema guardado
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light"
  document.documentElement.setAttribute("data-theme", savedTheme)
  updateThemeButton(savedTheme)
  enhanceSimplexTables()
  updateValorOptimoTheme(savedTheme)

  // Inicializar campos
  generarCamposVariables()
  agregarRestriccion()
})

function generarCamposVariables() {
  numVariables = Number.parseInt(document.getElementById("num_variables").value)

  // Actualizar nombres de variables por defecto
  nombresVariables = []
  for (let i = 1; i <= numVariables; i++) {
    nombresVariables.push(`x${i}`)
  }

  generarTablaVariables()
  generarTablaObjetivo()
  generarHeaderRestricciones()
  limpiarRestricciones()
}

function generarTablaVariables() {
  const header = document.getElementById("variables-header")
  const names = document.getElementById("variables-names")

  header.innerHTML = ""
  names.innerHTML = ""

  for (let i = 0; i < numVariables; i++) {
    // Header
    const th = document.createElement("th")
    th.className = "text-center"
    th.style.minWidth = "120px"
    th.innerHTML = `Variable ${i + 1}`
    header.appendChild(th)

    // Input
    const td = document.createElement("td")
    td.innerHTML = `
            <input type="text" class="form-control form-control-sm text-center variable-name-input" 
                   id="nombre_var_${i}" value="${nombresVariables[i]}" 
                   onchange="actualizarNombreVariable(${i}, this.value)"
                   placeholder="x${i + 1}">
        `
    names.appendChild(td)
  }
}

function generarTablaObjetivo() {
  const header = document.getElementById("objetivo-header")
  const coefs = document.getElementById("objetivo-coeficientes")

  header.innerHTML = ""
  coefs.innerHTML = ""

  for (let i = 0; i < numVariables; i++) {
    // Header
    const th = document.createElement("th")
    th.className = "text-center"
    th.style.minWidth = "120px"
    th.innerHTML = `<span id="obj_label_${i}">${nombresVariables[i]}</span>`
    header.appendChild(th)

    // Input
    const td = document.createElement("td")
    td.innerHTML = `
            <input type="number" class="form-control form-control-sm text-center objetivo-input" 
                   name="coef_obj_${i}" step="any" placeholder="0"
                   id="coef_obj_${i}">
        `
    coefs.appendChild(td)
  }
}

function generarHeaderRestricciones() {
  const header = document.getElementById("restricciones-header")

  // Limpiar header completamente
  header.innerHTML = ""

  // # columna
  const thNum = document.createElement("th")
  thNum.className = "text-center"
  thNum.style.minWidth = "60px"
  thNum.textContent = "#"
  header.appendChild(thNum)

  // Variables de restricción en orden
  for (let i = 0; i < numVariables; i++) {
    const th = document.createElement("th")
    th.className = "text-center"
    th.style.minWidth = "100px"
    th.innerHTML = `<span id="rest_label_${i}">${nombresVariables[i]}</span>`
    header.appendChild(th)
  }

  // Tipo
  const thTipo = document.createElement("th")
  thTipo.className = "text-center"
  thTipo.style.minWidth = "80px"
  thTipo.textContent = "Tipo"
  header.appendChild(thTipo)

  // Valor
  const thValor = document.createElement("th")
  thValor.className = "text-center"
  thValor.style.minWidth = "100px"
  thValor.textContent = "Valor"
  header.appendChild(thValor)

  // Acción
  const thAccion = document.createElement("th")
  thAccion.className = "text-center"
  thAccion.style.minWidth = "80px"
  thAccion.textContent = "Acción"
  header.appendChild(thAccion)
}

function actualizarNombreVariable(indice, nuevoNombre) {
  if (nuevoNombre.trim() === "") {
    nuevoNombre = `x${indice + 1}`
    document.getElementById(`nombre_var_${indice}`).value = nuevoNombre
  }

  nombresVariables[indice] = nuevoNombre

  // Actualizar etiquetas en función objetivo
  const objLabel = document.getElementById(`obj_label_${indice}`)
  if (objLabel) {
    objLabel.textContent = nuevoNombre
  }

  // Actualizar etiquetas en restricciones
  const restLabel = document.getElementById(`rest_label_${indice}`)
  if (restLabel) {
    restLabel.textContent = nuevoNombre
  }
}

function limpiarRestricciones() {
  const tbody = document.getElementById("restricciones-tbody")
  tbody.innerHTML = ""
  contadorRestricciones = 0
}

function agregarRestriccion() {
  const tbody = document.getElementById("restricciones-tbody")
  const tr = document.createElement("tr")
  tr.id = `restriccion_${contadorRestricciones}`
  tr.className = "restriccion-row"

  // Número de restricción
  let html = `<td class="text-center fw-bold">${contadorRestricciones + 1}</td>`

  // Coeficientes de variables
  for (let i = 0; i < numVariables; i++) {
    html += `
            <td>
                <input type="number" class="form-control form-control-sm text-center restriccion-input" 
                       name="restriccion_${contadorRestricciones}_coef_${i}" 
                       step="any" placeholder="0">
            </td>
        `
  }

  // Tipo de restricción
  html += `
        <td style="min-width:80px">
            <select class="form-select form-select-sm" 
                    name="restriccion_${contadorRestricciones}_tipo">
                <option value="<=">&le;</option>
                <option value=">=">&ge;</option>
                <option value="=">=</option>
            </select>
        </td>
    `

  // Valor
  html += `
        <td style="min-width:70px">
            <input type="number" class="form-control form-control-sm text-center restriccion-valor" 
                   name="restriccion_${contadorRestricciones}_valor" 
                   placeholder="0" step="any" required>
        </td>
    `

  // Botón eliminar
  html += `
        <td class="text-center">
            <button type="button" class="btn btn-outline-danger btn-sm" 
                    onclick="eliminarRestriccion(${contadorRestricciones})"
                    title="Eliminar restricción">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `

  tr.innerHTML = html
  tbody.appendChild(tr)

  // Animación de entrada
  tr.style.opacity = "0"
  tr.style.transform = "translateY(-10px)"
  setTimeout(() => {
    tr.style.transition = "all 0.3s ease"
    tr.style.opacity = "1"
    tr.style.transform = "translateY(0)"
  }, 10)

  contadorRestricciones++
}

function eliminarRestriccion(id) {
  const restriccion = document.getElementById(`restriccion_${id}`)
  if (restriccion) {
    restriccion.style.transition = "all 0.3s ease"
    restriccion.style.opacity = "0"
    restriccion.style.transform = "translateY(-10px)"
    setTimeout(() => {
      restriccion.remove()
      actualizarNumeracionRestricciones()
    }, 300)
  }
}

function actualizarNumeracionRestricciones() {
  const filas = document.querySelectorAll(".restriccion-row")
  filas.forEach((fila, index) => {
    const numeroCell = fila.querySelector("td:first-child")
    if (numeroCell) {
      numeroCell.textContent = index + 1
    }
  })
}

function cargarEjemplo() {
  // Configurar 2 variables
  document.getElementById("num_variables").value = "2"
  document.getElementById("maximizar").checked = true

  generarCamposVariables()

  // Configurar función objetivo: 3x₁ + 2x₂
  document.getElementById("coef_obj_0").value = "3"
  document.getElementById("coef_obj_1").value = "2"

  // Limpiar restricciones existentes
  limpiarRestricciones()

  agregarRestriccion()
  const rest1 = document.querySelector('[name="restriccion_0_coef_0"]')
  const rest1_2 = document.querySelector('[name="restriccion_0_coef_1"]')
  const rest1_tipo = document.querySelector('[name="restriccion_0_tipo"]')
  const rest1_valor = document.querySelector('[name="restriccion_0_valor"]')

  if (rest1) rest1.value = "1"
  if (rest1_2) rest1_2.value = "1"
  if (rest1_tipo) rest1_tipo.value = "<="
  if (rest1_valor) rest1_valor.value = "4"

  agregarRestriccion()
  const rest2 = document.querySelector('[name="restriccion_1_coef_0"]')
  const rest2_2 = document.querySelector('[name="restriccion_1_coef_1"]')
  const rest2_tipo = document.querySelector('[name="restriccion_1_tipo"]')
  const rest2_valor = document.querySelector('[name="restriccion_1_valor"]')

  if (rest2) rest2.value = "2"
  if (rest2_2) rest2_2.value = "1"
  if (rest2_tipo) rest2_tipo.value = "<="
  if (rest2_valor) rest2_valor.value = "6"

  showNotification("Ejemplo cargado: Maximizar 3x₁ + 2x₂ con 2 restricciones", "success")
  // Actualizar la sección de problema actual
  setTimeout(actualizarProblemaActual, 20)
}

function limpiarFormulario() {
  // Confirmar antes de limpiar
  if (window.Swal) {
    window.Swal.fire({
      title: "¿Limpiar formulario?",
      text: "Se perderán todos los datos ingresados",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Sí, limpiar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        ejecutarLimpiezaFormulario()
        showNotification("Formulario limpiado correctamente", "info")
      }
    })
  } else {
    if (confirm("¿Está seguro de que desea limpiar todo el formulario?")) {
      ejecutarLimpiezaFormulario()
    }
  }
}

function ejecutarLimpiezaFormulario() {
  // Resetear a valores por defecto
  document.getElementById("num_variables").value = "2"
  document.getElementById("maximizar").checked = true

  // Regenerar campos
  generarCamposVariables()

  // Limpiar función objetivo
  for (let i = 0; i < numVariables; i++) {
    const input = document.getElementById(`coef_obj_${i}`)
    if (input) input.value = ""
  }

  // Limpiar restricciones
  limpiarRestricciones()
  agregarRestriccion() // Agregar una restricción vacía

  // Actualizar problema actual
  setTimeout(actualizarProblemaActual, 20)
}

function showNotification(message, type = "info") {
  let icon = type
  if (type === "danger") icon = "error"
  if (type === "primary") icon = "info"
  if (type === "secondary") icon = "info"
  if (type === "warning") icon = "warning"
  if (type === "success") icon = "success"
  if (type === "info") icon = "info"

  window.Swal.fire({
    toast: true,
    position: "top-end",
    icon: icon,
    title: message,
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    customClass: {
      popup: "swal2-shadow",
    },
  })
}

// Interceptar el envío del formulario para procesar los datos
document.addEventListener("submit", (e) => {
  if (e.target.id === "simplexForm") {
    procesarFormulario(e)
  }
})

function procesarFormulario(e) {
  // Recopilar coeficientes de la función objetivo
  const coeficientesObj = []
  for (let i = 0; i < numVariables; i++) {
    const input = document.getElementById(`coef_obj_${i}`)
    const valor = Number.parseFloat(input.value) || 0
    coeficientesObj.push(valor)
  }

  // Crear campo oculto con los coeficientes
  const inputCoefObj = document.createElement("input")
  inputCoefObj.type = "hidden"
  inputCoefObj.name = "funcion_objetivo"
  inputCoefObj.value = coeficientesObj.join(",")
  e.target.appendChild(inputCoefObj)

  //campo oculto con los nombres de variables
  const inputNombres = document.createElement("input")
  inputNombres.type = "hidden"
  inputNombres.name = "nombres_variables"
  inputNombres.value = nombresVariables.join(",")
  e.target.appendChild(inputNombres)

  // Procesar restricciones
  const restricciones = document.querySelectorAll(".restriccion-row")
  restricciones.forEach((restriccion, index) => {
    const coeficientes = []
    for (let i = 0; i < numVariables; i++) {
      const input = restriccion.querySelector(`[name$="_coef_${i}"]`)
      const valor = Number.parseFloat(input.value) || 0
      coeficientes.push(valor)
    }

    // Crear campo oculto con coeficientes de la restricción
    const inputRestCoef = document.createElement("input")
    inputRestCoef.type = "hidden"
    inputRestCoef.name = `restriccion_${index}_coeficientes`
    inputRestCoef.value = coeficientes.join(",")
    e.target.appendChild(inputRestCoef)
  })
}

// Actualiza la sección de "Problema actual Ingresado" con los datos actuales
function actualizarProblemaActual() {
  // Obtener tipo de optimización
  const tipoOpt = document.querySelector('input[name="tipo_optimizacion"]:checked')?.value || "maximizar"
  // Obtener nombres de variables
  const nombres = nombresVariables
  // Obtener coeficientes de la función objetivo
  const coefs = []
  for (let i = 0; i < numVariables; i++) {
    const input = document.getElementById(`coef_obj_${i}`)
    coefs.push(Number.parseFloat(input?.value) || 0)
  }
  // Construir función objetivo
  let objStr = (tipoOpt === "maximizar" ? "Maximizar" : "Minimizar") + " "
  objStr += coefs
    .map((c, i) => {
      const sign = c >= 0 && i > 0 ? " + " : c < 0 ? " - " : ""
      return (i > 0 ? sign : c < 0 ? "-" : "") + Math.abs(c) + nombres[i]
    })
    .join("")

  // Obtener restricciones
  const restricciones = []
  const filas = document.querySelectorAll(".restriccion-row")
  filas.forEach((fila, idx) => {
    let restr = ""
    for (let i = 0; i < numVariables; i++) {
      const input = fila.querySelector(`[name$="_coef_${i}"]`)
      const val = Number.parseFloat(input?.value) || 0
      restr += (i > 0 ? (val >= 0 ? " + " : " - ") : val < 0 ? "-" : "") + Math.abs(val) + nombres[i]
    }
    const tipo = fila.querySelector("select")?.value || "<="
    const valor = fila.querySelector(".restriccion-valor")?.value || "0"
    restr += ` ${tipo} ${valor}`
    restricciones.push(restr)
  })

  // Variables no negativas
  const varsNoNeg = nombres.join(", ") + " ≥ 0"

  // Renderizar en el contenedor
  const cont = document.getElementById("problema-actual")
  if (cont) {
    cont.innerHTML = `
      <h6 class="text-primary mb-2">
        <i class="fas fa-lightbulb me-1"></i>Problema actual Ingresado
      </h6>
      <div class="small">
        <p class="mb-2"><strong>Problema:</strong> ${objStr}</p>
        <p class="mb-2"><strong>Sujeto a:</strong></p>
        <ul class="mb-2 ps-3">
          ${restricciones.map((r) => `<li>${r}</li>`).join("")}
          <li>${varsNoNeg}</li>
        </ul>
      </div>
    `
  }
}
// Llama a actualizarProblemaActual en cada cambio relevante
;["input", "change"].forEach((evt) => {
  document.addEventListener(evt, (e) => {
    if (
      e.target.matches(
        '.objetivo-input, .variable-name-input, .restriccion-input, .restriccion-valor, select[name^="restriccion_"]',
      ) ||
      e.target.id === "num_variables" ||
      e.target.name === "tipo_optimizacion"
    ) {
      setTimeout(actualizarProblemaActual, 10)
    }
  })
})

function enhanceSimplexTables() {
  // Buscar todas las tablas Simplex y mejorar su visualización
  const tables = document.querySelectorAll(".simplex-table")

  tables.forEach((table, tableIndex) => {
    const rows = table.querySelectorAll("tbody tr")

    // Detectar información de pivote desde los pasos
    const pasos = document.querySelectorAll(".solution-steps p, .solution-steps .alert")
    let filaPivote = -1
    let columnaPivote = -1

    // Buscar información de pivote en los pasos
    pasos.forEach((paso) => {
      const texto = paso.textContent || paso.innerText

      // Buscar variable entrante (columna pivote)
      const matchEntrante = texto.match(/VARIABLE ENTRANTE:.*columna (\d+)/)
      if (matchEntrante) {
        columnaPivote = Number.parseInt(matchEntrante[1]) - 1 // Convertir a índice base 0
      }

      // Buscar variable saliente (fila pivote)
      const matchSaliente = texto.match(/VARIABLE SALIENTE:.*fila (\d+)/)
      if (matchSaliente) {
        filaPivote = Number.parseInt(matchSaliente[1]) - 1 // Convertir a índice base 0
      }
    })

    // Aplicar estilos de pivote si se encontraron
    if (filaPivote >= 0 && columnaPivote >= 0) {
      highlightPivotElements(table, filaPivote, columnaPivote)
    }

    // Marcar la última fila como fila objetivo
    rows.forEach((row, rowIndex) => {
      const cells = row.querySelectorAll("td")

      if (cells.length > 0 && cells[0].textContent.trim() === "Z") {
        row.classList.add("objective-row")
      }
    })

    // Agregar hover effects mejorados
    addHoverEffects(table)
  })
}

function highlightPivotElements(table, pivotRow, pivotCol) {
  const rows = table.querySelectorAll("tbody tr")

  // Resaltar columna entrante (excluyendo fila objetivo)
  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("td")
    if (cells[pivotCol + 1] && !row.classList.contains("objective-row")) {
      // +1 porque la primera columna es la base
      cells[pivotCol + 1].classList.add("entering-variable")
    }
  })

  // Resaltar fila saliente
  if (rows[pivotRow]) {
    const cells = rows[pivotRow].querySelectorAll("td")
    cells.forEach((cell, cellIndex) => {
      if (cellIndex > 0) {
        // Excluir columna base
        cell.classList.add("leaving-variable")
      }
    })
    rows[pivotRow].classList.add("pivot-row")
  }

  // Resaltar elemento pivote
  if (rows[pivotRow] && rows[pivotRow].querySelectorAll("td")[pivotCol + 1]) {
    const pivotCell = rows[pivotRow].querySelectorAll("td")[pivotCol + 1]
    pivotCell.classList.add("pivot-cell")

    // Agregar tooltip con información del pivote
    pivotCell.title = `Elemento Pivote: ${pivotCell.textContent.trim()}`
  }

  // Resaltar encabezados de columna y fila pivote
  const headers = table.querySelectorAll("thead th")
  if (headers[pivotCol + 1]) {
    headers[pivotCol + 1].style.backgroundColor = "#007bff"
    headers[pivotCol + 1].style.color = "white"
  }
}

function addHoverEffects(table) {
  const cells = table.querySelectorAll("td")

  cells.forEach((cell) => {
    cell.addEventListener("mouseenter", function () {
      // Resaltar fila y columna al hacer hover
      const row = this.parentElement
      const cellIndex = Array.from(row.children).indexOf(this)

      // Resaltar fila
      Array.from(row.children).forEach((c) => {
        c.style.backgroundColor = "rgba(0, 123, 255, 0.1)"
      })

      // Resaltar columna
      const table = row.closest("table")
      const rows = table.querySelectorAll("tr")
      rows.forEach((r) => {
        if (r.children[cellIndex]) {
          if (document.documentElement.getAttribute("data-theme") === "dark") {
            r.children[cellIndex].style.backgroundColor = "rgba(0, 123, 255, 0.1)"
          } else {
            r.children[cellIndex].style.backgroundColor = "rgba(0, 60, 130, 0.18)"
          }
        }
      })
    })

    cell.addEventListener("mouseleave", function () {
      // Restaurar colores originales
      const row = this.parentElement
      const cellIndex = Array.from(row.children).indexOf(this)

      // Restaurar fila
      Array.from(row.children).forEach((c) => {
        c.style.backgroundColor = ""
      })

      // Restaurar columna
      const table = row.closest("table")
      const rows = table.querySelectorAll("tr")
      rows.forEach((r) => {
        if (r.children[cellIndex]) {
          r.children[cellIndex].style.backgroundColor = ""
        }
      })
    })
  })
}

// Validación en tiempo real
document.addEventListener("input", (e) => {
  if (e.target.type === "number") {
    validateNumber(e.target)
  }
})

function validateNumber(input) {
  const value = input.value.trim()
  if (value && isNaN(Number.parseFloat(value))) {
    input.classList.add("is-invalid")
    showTooltip(input, "Debe ser un número válido")
  } else {
    input.classList.remove("is-invalid")
    input.classList.add("is-valid")
    hideTooltip(input)
  }
}

function showTooltip(element, message) {
  element.title = message
}

function hideTooltip(element) {
  element.title = ""
}

document.addEventListener("DOMContentLoaded", () => {
  // Animación de entrada para las tarjetas
  const cards = document.querySelectorAll(".card")
  cards.forEach((card, index) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(20px)"
    setTimeout(() => {
      card.style.transition = "all 0.5s ease"
      card.style.opacity = "1"
      card.style.transform = "translateY(0)"
    }, index * 100)
  })
})

// Función para repoblar campos después de resolver
function repoblarCampos() {
  // Esta función se ejecuta cuando hay datos previos que mantener
  const mantenerDatos = document.querySelector("[data-mantener-datos]")
  if (!mantenerDatos) return

  // Obtener datos del template
  const datosTemplate = window.datosSimplexTemplate || {}

  if (datosTemplate.num_variables) {
    document.getElementById("num_variables").value = datosTemplate.num_variables
    generarCamposVariables()
  }

  if (datosTemplate.tipo_optimizacion) {
    const radioBtn = document.getElementById(datosTemplate.tipo_optimizacion)
    if (radioBtn) radioBtn.checked = true
  }

  // Repoblar nombres de variables
  if (datosTemplate.nombres_variables) {
    datosTemplate.nombres_variables.forEach((nombre, index) => {
      const input = document.getElementById(`nombre_var_${index}`)
      if (input) {
        input.value = nombre
        actualizarNombreVariable(index, nombre)
      }
    })
  }

  // Repoblar función objetivo
  if (datosTemplate.funcion_objetivo_valores) {
    datosTemplate.funcion_objetivo_valores.forEach((valor, index) => {
      const input = document.getElementById(`coef_obj_${index}`)
      if (input) input.value = valor
    })
  }

  // Limpiar restricciones existentes
  limpiarRestricciones()

  // Repoblar restricciones
  if (datosTemplate.restricciones_data) {
    datosTemplate.restricciones_data.forEach((restriccion, index) => {
      agregarRestriccion()

      // Llenar coeficientes
      restriccion.coeficientes.forEach((coef, coefIndex) => {
        const input = document.querySelector(`[name="restriccion_${index}_coef_${coefIndex}"]`)
        if (input) input.value = coef
      })

      // Llenar tipo
      const selectTipo = document.querySelector(`[name="restriccion_${index}_tipo"]`)
      if (selectTipo) selectTipo.value = restriccion.tipo

      // Llenar valor
      const inputValor = document.querySelector(`[name="restriccion_${index}_valor"]`)
      if (inputValor) inputValor.value = restriccion.valor
    })
  }

  // Actualizar problema actual
  setTimeout(actualizarProblemaActual, 100)
}

// Ejecutar repoblado cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
  // Delay para asegurar que todos los elementos estén listos
  setTimeout(repoblarCampos, 200)
})