// Configuración y funciones para MathLive
document.addEventListener("DOMContentLoaded", () => {
  initializeMathLive()
})

function initializeMathLive() {
  const mathField = document.getElementById("funcion")
  if (!mathField) return

  // Configurar MathLive
  mathField.addEventListener("input", (ev) => {
    // Convertir LaTeX a formato Python
    const latex = ev.target.value
    const pythonExpr = convertLatexToPython(latex)

    // Actualizar el campo oculto
    const hiddenField = document.getElementById("funcion-hidden")
    if (hiddenField) {
      hiddenField.value = pythonExpr
    }

    // Mostrar preview
    updatePreview(latex, pythonExpr)
  })

  // Configurar opciones del teclado virtual
  mathField.setOptions({
    virtualKeyboardMode: "manual",
    virtualKeyboards: "numeric functions symbols greek",
    customVirtualKeyboardLayers: {
      custom: {
        label: "Funciones",
        tooltip: "Funciones matemáticas",
        rows: [
          [
            { latex: "\\sin", insert: "\\sin\\left(#0\\right)" },
            { latex: "\\cos", insert: "\\cos\\left(#0\\right)" },
            { latex: "\\tan", insert: "\\tan\\left(#0\\right)" },
            { latex: "\\ln", insert: "\\ln\\left(#0\\right)" },
          ],
          [
            { latex: "\\log", insert: "\\log\\left(#0\\right)" },
            { latex: "e^{#0}", insert: "e^{#0}" },
            { latex: "\\sqrt{#0}", insert: "\\sqrt{#0}" },
            { latex: "|#0|", insert: "\\left|#0\\right|" },
          ],
        ],
      },
    },
  })

  // Establecer valor inicial si existe
  const initialValue = mathField.getAttribute("data-initial") || mathField.textContent
  if (initialValue) {
    mathField.value = convertPythonToLatex(initialValue)
  }
}

function convertLatexToPython(latex) {
  if (!latex) return ""

  let python = latex

  // Limpiar comandos LaTeX básicos primero
  python = python.replace(/\\left\(/g, "(")
  python = python.replace(/\\right\)/g, ")")
  python = python.replace(/\\left\{/g, "(")
  python = python.replace(/\\right\}/g, ")")
  python = python.replace(/\{/g, "(")
  python = python.replace(/\}/g, ")")

  // Conversiones de funciones trigonométricas e hiperbólicas
  python = python.replace(/\\sin\s*\(/g, "sin(")
  python = python.replace(/\\cos\s*\(/g, "cos(")
  python = python.replace(/\\tan\s*\(/g, "tan(")
  python = python.replace(/\\sec\s*\(/g, "1/cos(")
  python = python.replace(/\\csc\s*\(/g, "1/sin(")
  python = python.replace(/\\cot\s*\(/g, "1/tan(")

  // Funciones inversas
  python = python.replace(/\\arcsin\s*\(/g, "asin(")
  python = python.replace(/\\arccos\s*\(/g, "acos(")
  python = python.replace(/\\arctan\s*\(/g, "atan(")

  // Funciones hiperbólicas
  python = python.replace(/\\sinh\s*\(/g, "sinh(")
  python = python.replace(/\\cosh\s*\(/g, "cosh(")
  python = python.replace(/\\tanh\s*\(/g, "tanh(")

  // Funciones logarítmicas
  python = python.replace(/\\ln\s*\(/g, "log(")
  python = python.replace(/\\log\s*\(/g, "log10(")

  // Exponencial
  python = python.replace(/\\exp\s*\(/g, "exp(")
  python = python.replace(/e\^/g, "exp(")

  // Raíz cuadrada
  python = python.replace(/\\sqrt\s*\(/g, "sqrt(")

  // Valor absoluto
  python = python.replace(/\\left\|/g, "abs(")
  python = python.replace(/\\right\|/g, ")")

  // Potencias - manejar diferentes formatos
  python = python.replace(/\^/g, "**")
  python = python.replace(/\*\*/g, "**") // Evitar doble conversión

  // Constantes matemáticas
  python = python.replace(/\\pi/g, "pi")
  python = python.replace(/\\e/g, "E")

  // Fracciones simples
  python = python.replace(/\\frac\s*$$\s*([^,]+)\s*,\s*([^)]+)\s*$$/g, "($1)/($2)")

  // Limpiar asteriscos extra que pueden aparecer
  // Solo reemplazar 3 o más asteriscos por uno, para no romper potencias
  python = python.replace(/\*{3,}/g, "*")

  // Multiplicación implícita
  python = python.replace(/(\d)([a-zA-Z])/g, "$1*$2")
  python = python.replace(/([a-zA-Z])(\d)/g, "$1*$2")
  python = python.replace(/\)\(/g, ")*(")
  python = python.replace(/\)([a-zA-Z])/g, ")*$1")
  python = python.replace(/([a-zA-Z])\(/g, "$1*(")

  // Limpiar espacios
  python = python.replace(/\s+/g, "")

  return python
}

function convertPythonToLatex(python) {
  if (!python) return ""

  let latex = python

  // Conversiones básicas
  latex = latex.replace(/\*\*/g, "^")

  // Funciones trigonométricas
  latex = latex.replace(/sin\(/g, "\\sin(")
  latex = latex.replace(/cos\(/g, "\\cos(")
  latex = latex.replace(/tan\(/g, "\\tan(")

  // Funciones logarítmicas
  latex = latex.replace(/log\(/g, "\\ln(")
  latex = latex.replace(/log10\(/g, "\\log(")

  // Exponencial
  latex = latex.replace(/exp\(/g, "\\exp(")

  // Raíz cuadrada
  latex = latex.replace(/sqrt\(/g, "\\sqrt{")

  // Valor absoluto
  latex = latex.replace(/abs\(/g, "\\left|")

  // Constantes
  latex = latex.replace(/pi/g, "\\pi")
  latex = latex.replace(/E/g, "e")

  return latex
}

function updatePreview(latex, python) {
  // Crear o actualizar preview
  let preview = document.getElementById("function-preview")
  if (!preview) {
    preview = document.createElement("div")
    preview.id = "function-preview"
    preview.className = "mt-2 p-2 bg-light rounded small"

    const mathField = document.getElementById("funcion")
    mathField.parentNode.insertBefore(preview, mathField.nextSibling)
  }

  preview.innerHTML = `
        <strong>Vista previa:</strong><br>
        <span class="text-muted">LaTeX:</span> <code>${latex}</code><br>
        <span class="text-muted">Python:</span> <code>${python}</code>
    `
}

function toggleMathKeyboard() {
  const mathField = document.getElementById("funcion")
  if (mathField) {
    if (mathField.virtualKeyboardState === "hidden") {
      mathField.executeCommand("showVirtualKeyboard")
    } else {
      mathField.executeCommand("hideVirtualKeyboard")
    }
  }
}

// Funciones de ejemplo para insertar
function insertFunction(func) {
  const mathField = document.getElementById("funcion")
  if (mathField) {
    mathField.executeCommand(["insert", func])
    mathField.focus()
  }
}

// Ejemplos predefinidos
const mathExamples = {
  polynomial: "x^2+2*x+1",
  trigonometric: "\\sin(x)",
  exponential: "\\exp(x)",
  logarithmic: "\\ln(x)",
  rational: "\\frac{1}{1+x^2}",
}

function loadExample(type) {
  const mathField = document.getElementById("funcion")
  if (mathField && mathExamples[type]) {
    mathField.value = mathExamples[type]
    mathField.dispatchEvent(new Event("input"))
  }
}
