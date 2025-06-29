// Variables globales
let contadorRestricciones = 0
let numVariables = 3
let nombresVariables = ["x₁", "x₂", "x₃"]

// Función para alternar tema
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme")
  const newTheme = currentTheme === "dark" ? "light" : "dark"
  document.documentElement.setAttribute("data-theme", newTheme)
  localStorage.setItem("theme", newTheme)
  updateThemeButton(newTheme)
}

// Actualiza el icono y las clases del botón según el tema
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
    body.classList.add("bg-secondary-neon")
  } else {
    if (icon) icon.className = "fas fa-moon"
    if (boton) {
      boton.classList.remove("bg-warning-neon")
      boton.classList.add("bg-secondary-neon")
    }
    body.classList.remove("bg-secondary-neon")
  }
}

// Cargar tema guardado
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light"
  document.documentElement.setAttribute("data-theme", savedTheme)
  updateThemeButton(savedTheme)
  enhanceSimplexTables()

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

  generarCamposNombres()
  generarCamposFuncionObjetivo()
  limpiarRestricciones()
}

function generarCamposNombres() {
  const container = document.getElementById("nombres-variables-container")
  container.innerHTML = ""
  container.className = `row row-cols-${Math.min(numVariables, 6)} flex-nowrap` // Responsive y scroll

  for (let i = 0; i < numVariables; i++) {
    const div = document.createElement("div")
    div.className = `col mb-2`
    div.innerHTML = `
            <input type="text" class="form-control form-control-sm text-center" 
                   id="nombre_var_${i}" value="${nombresVariables[i]}" 
                   onchange="actualizarNombreVariable(${i}, this.value)"
                   placeholder="x₁${i + 1}">
            <small class="text-muted">Var ${i + 1}</small>
        `
    container.appendChild(div)
  }
}

function generarCamposFuncionObjetivo() {
  const container = document.getElementById("funcion-objetivo-container")
  container.innerHTML = ""
  container.className = `row row-cols-${Math.min(numVariables, 6)} flex-nowrap` // Responsive y scroll

  for (let i = 0; i < numVariables; i++) {
    const div = document.createElement("div")
    div.className = `col mb-2`
    div.innerHTML = `
            <div class="input-group input-group-sm">
                <input type="number" class="form-control" 
                       name="coef_obj_${i}" step="any" placeholder="0"
                       id="coef_obj_${i}">
                <span class="input-group-text" id="label_var_${i}">${nombresVariables[i]}</span>
            </div>
        `
    container.appendChild(div)
  }
}

function actualizarNombreVariable(indice, nuevoNombre) {
  if (nuevoNombre.trim() === "") {
    nuevoNombre = `x₁${indice + 1}`
    document.getElementById(`nombre_var_${indice}`).value = nuevoNombre
  }

  nombresVariables[indice] = nuevoNombre

  // Actualizar etiquetas en función objetivo
  const label = document.getElementById(`label_var_${indice}`)
  if (label) {
    label.textContent = nuevoNombre
  }

  // Actualizar etiquetas en restricciones existentes
  actualizarEtiquetasRestricciones()
}

function actualizarEtiquetasRestricciones() {
  const restricciones = document.querySelectorAll('[id^="restriccion_"]')
  restricciones.forEach((restriccion) => {
    const labels = restriccion.querySelectorAll(".input-group-text")
    labels.forEach((label, index) => {
      if (index < nombresVariables.length) {
        label.textContent = nombresVariables[index]
      }
    })
  })
}

function limpiarRestricciones() {
  const container = document.getElementById("restricciones-container")
  container.innerHTML = ""
  contadorRestricciones = 0
}

function agregarRestriccion() {
  const container = document.getElementById("restricciones-container")
  const div = document.createElement("div")
  div.className = "mb-3 p-3 border rounded"
  div.id = `restriccion_${contadorRestricciones}`

  let coeficientesHTML = ""
  for (let i = 0; i < numVariables; i++) {
    coeficientesHTML += `
            <div class="col mb-2">
                <div class="input-group input-group-sm p-0">
                    <input type="number" class="form-control" 
                           name="restriccion_${contadorRestricciones}_coef_${i}" 
                           step="any" placeholder="0">
                    <span class="input-group-text p-0 p-1">${nombresVariables[i]}</span>
                </div>
            </div>
        `
  }

  div.innerHTML = `
        <div class="row row-cols-${Math.min(numVariables + 2, 8)} align-items-end flex-nowrap">
            ${coeficientesHTML}
            <div class="col mb-2">
                <select class="form-select form-select-sm" 
                        name="restriccion_${contadorRestricciones}_tipo">
                    <option value="<=" >&le;</option>
                    <option value=">=" >&ge;</option>
                    <option value="=" >=</option>
                </select>
            </div>
            <div class="col mb-2">
                <input type="number" class="form-control form-control-sm" 
                       name="restriccion_${contadorRestricciones}_valor" 
                       placeholder="0" step="any" required>
            </div>
            <div class="col-12 col-md-auto mb-2">
                <button type="button" class="btn btn-outline-danger btn-sm w-100" 
                        onclick="eliminarRestriccion(${contadorRestricciones})">
                    <i class="fas fa-trash me-1"></i>Eliminar
                </button>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <small class="text-muted">Restricción ${contadorRestricciones + 1}</small>
            </div>
        </div>
    `

  container.appendChild(div)
  contadorRestricciones++
}

function eliminarRestriccion(id) {
  const restriccion = document.getElementById(`restriccion_${id}`)
  if (restriccion) {
    restriccion.remove()
  }
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

  // Crear campo oculto con los nombres de variables
  const inputNombres = document.createElement("input")
  inputNombres.type = "hidden"
  inputNombres.name = "nombres_variables"
  inputNombres.value = nombresVariables.join(",")
  e.target.appendChild(inputNombres)

  // Procesar restricciones
  const restricciones = document.querySelectorAll('[id^="restriccion_"]')
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
          // Usar un color más oscuro en modo claro
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
    hideTooltip(input)
  }
}

function showTooltip(element, message) {
  element.title = message
}

function hideTooltip(element) {
  element.title = ""
}