// Configuración y funciones para gráficas de Hermite con Plotly
let currentPlot = null
let isDragging = false

function initializeHermiteGraph(datosGrafica) {
  if (!datosGrafica) return

  const graphDiv = document.getElementById("hermite-graph")
  if (!graphDiv) return

  // Configurar trazas
  const traces = [
    // Curva del polinomio
    {
      x: datosGrafica.curva_x,
      y: datosGrafica.curva_y,
      type: "scatter",
      mode: "lines",
      name: "Polinomio de Hermite",
      line: {
        color: "#007bff",
        width: 3,
      },
      hovertemplate: "H(%{x:.3f}) = %{y:.3f}<extra></extra>",
    },
    // Puntos de interpolación
    {
      x: datosGrafica.puntos_x,
      y: datosGrafica.puntos_y,
      type: "scatter",
      mode: "markers+text",
      name: "Puntos de interpolación",
      marker: {
        color: "#28a745",
        size: 12,
        symbol: "circle",
        line: {
          color: "#ffffff",
          width: 2,
        },
      },
      text: datosGrafica.puntos_x.map(
        (x, i) => `P${i + 1}(${x}, ${datosGrafica.puntos_y[i]})<br>f'(${x}) = ${datosGrafica.derivadas[i]}`,
      ),
      textposition: "top center",
      textfont: {
        size: 10,
        color: "#28a745",
      },
      hovertemplate:
        "Punto: (%{x}, %{y})<br>Derivada: " +
        datosGrafica.derivadas.map((d) => d.toFixed(3)).join(", ") +
        "<extra></extra>",
      // Hacer los puntos arrastrables
      //dragmode: "select",
    },
    // Punto de evaluación
    {
      x: [datosGrafica.eval_x],
      y: [datosGrafica.eval_y],
      type: "scatter",
      mode: "markers+text",
      name: "Punto de evaluación",
      marker: {
        color: "#dc3545",
        size: 15,
        symbol: "diamond",
        line: {
          color: "#ffffff",
          width: 2,
        },
      },
      text: [`Evaluación<br>x=${datosGrafica.eval_x}<br>H(x)=${datosGrafica.eval_y.toFixed(6)}`],
      textposition: "top center",
      textfont: {
        size: 10,
        color: "#dc3545",
      },
      hovertemplate: "Evaluación: x=%{x}<br>H(x)=%{y:.6f}<extra></extra>",
    },
  ]

  // Configuración del layout
  const layout = {
    title: {
      text: "Interpolación de Hermite - Gráfica Interactiva",
      font: { size: 16, color: "#333" },
    },
    xaxis: {
      title: "x",
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
      range: [datosGrafica.x_min, datosGrafica.x_max],
    },
    yaxis: {
      title: "f(x)",
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
      range: [datosGrafica.y_min, datosGrafica.y_max],
    },
    plot_bgcolor: "#fafafa",
    paper_bgcolor: "#ffffff",
    showlegend: true,
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: "rgba(255,255,255,0.8)",
      bordercolor: "#ccc",
      borderwidth: 1,
    },
    dragmode: "pan",
    hovermode: "closest",
    margin: { t: 50, r: 50, b: 50, l: 50 },
  }

  // Configuración
  const config = {
    displayModeBar: true,
    modeBarButtonsToAdd: [
      {
        name: "Editar puntos del problema",
        icon: {
          width: 857.1,
          height: 1000,
          path: "M857.1 428.6c0-204.8-166.3-371.4-371.4-371.4S114.3 223.8 114.3 428.6c0 204.8 166.3 371.4 371.4 371.4S857.1 633.4 857.1 428.6zM428.6 742.9c-173.1 0-314.3-141.1-314.3-314.3S255.4 114.3 428.6 114.3 742.9 255.4 742.9 428.6 601.7 742.9 428.6 742.9zM514.3 371.4V285.7c0-15.8-12.8-28.6-28.6-28.6s-28.6 12.8-28.6 28.6v114.3c0 15.8 12.8 28.6 28.6 28.6h85.7c15.8 0 28.6-12.8 28.6-28.6s-12.8-28.6-28.6-28.6H514.3z",
        },
        click: () => {
          regenerarPolinomio()
        },
      },
    ],
    modeBarButtonsToRemove: ["select2d", "lasso2d"],
    responsive: true,
  }

  // Crear gráfica
  Plotly.newPlot(graphDiv, traces, layout, config)
  currentPlot = graphDiv

  // Forzar resize tras renderizado inicial
  setTimeout(() => { Plotly.Plots.resize(graphDiv) }, 100);

  // Ajuste automático con ResizeObserver
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(() => {
      Plotly.Plots.resize(graphDiv)
    })
    ro.observe(graphDiv)
  } else {
    // Fallback: ajustar al redimensionar ventana
    window.addEventListener('resize', () => Plotly.Plots.resize(graphDiv))
  }

  // Agregar event listeners para arrastrar puntos
  setupDragEvents(graphDiv, datosGrafica)

  // Mostrar instrucciones
  showGraphInstructions()
}

function setupDragEvents(graphDiv, datosGrafica) {
  let dragPointIndex = -1

  // Detectar inicio de arrastre
  graphDiv.on("plotly_click", (data) => {
    if (data.points && data.points.length > 0) {
      const point = data.points[0]
      // Solo permitir arrastrar los puntos de interpolación (trace 1)
      if (point.curveNumber === 1) {
        dragPointIndex = point.pointNumber
        isDragging = true
        graphDiv.style.cursor = "grabbing"
      }
    }
  })

  // Detectar movimiento durante arrastre
  graphDiv.on("plotly_hover", (data) => {
    if (isDragging && dragPointIndex >= 0 && data.points && data.points.length > 0) {
      const newX = data.points[0].x
      const newY = data.points[0].y

      // Actualizar posición del punto
      updatePointPosition(dragPointIndex, newX, newY)
    }
  })

  // Finalizar arrastre
  document.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false
      dragPointIndex = -1
      if (currentPlot) {
        currentPlot.style.cursor = "default"
      }
    }
  })
}

function updatePointPosition(pointIndex, newX, newY) {
  if (!currentPlot) return

  // Actualizar datos del punto
  const update = {
    x: [[newX]],
    y: [[newY]],
  }

  Plotly.restyle(currentPlot, update, [1], [pointIndex])
}

function regenerarPolinomio() {
  if (!currentPlot) return

  // Obtener posiciones actuales de los puntos
  const puntosActuales = currentPlot.data[1]
  const nuevosX = puntosActuales.x
  const nuevosY = puntosActuales.y

  // Obtener derivadas originales (por simplicidad, mantener las mismas)
  const derivadasOriginales = window.datosGraficaHermite ? window.datosGraficaHermite.derivadas : [1, 1]

  // Crear nuevos puntos en formato esperado
  const nuevosPuntos = nuevosX.map((x, i) => [x, nuevosY[i], derivadasOriginales[i] || 1])

  // Mostrar modal de confirmación
  showRegenerateModal(nuevosPuntos)
}

function showRegenerateModal(nuevosPuntos) {
  let html = `
    <div class="table-responsive">
      <table class="table table-sm table-bordered table-striped" style="background: #f8f9fa; border-radius: 8px;">
        <thead style="background: #007bff; color: #fff;">
          <tr>
            <th>Punto</th>
            <th>x</th>
            <th>f(x)</th>
            <th>f'(x)</th>
          </tr>
        </thead>
        <tbody>
          ${nuevosPuntos
            .map(
              (p, i) => `
                <tr>
                  <td>P${i + 1}</td>
                  <td><input type="number" class="form-control form-control-sm x-input" value="${p[0]}" step="any" data-index="${i}" style="background:#e3f2fd; border:1px solid #90caf9;"></td>
                  <td><input type="number" class="form-control form-control-sm fx-input" value="${p[1]}" step="any" data-index="${i}" style="background:#e8f5e9; border:1px solid #a5d6a7;"></td>
                  <td><input type="number" class="form-control form-control-sm derivada-input" value="${p[2]}" step="any" data-index="${i}" style="background:#fff3e0; border:1px solid #ffcc80;"></td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `

  Swal.fire({
    title: '<span style="color:#1565c0;font-weight:bold;">Regenerar Polinomio</span>',
    icon: 'question',
    html: `
      <p style="color:#333;">¿Deseas regenerar el polinomio con las nuevas posiciones de los puntos?</p>
      ${html}
    `,
    background: 'white',
    customClass: {
      confirmButton: 'swal2-confirm btn btn-success',
      cancelButton: 'swal2-cancel btn btn-secondary',
      popup: 'swal2-modal-custom',
    },
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-sync-alt"></i> Regenerar',
    cancelButtonText: '<i class="fas fa-times"></i> Cancelar',
    reverseButtons: true,
    didOpen: () => {
      // Guardar referencia para la confirmación
      window.nuevosPuntosModal = nuevosPuntos
    }
  }).then((result) => {
    if (result.isConfirmed) {
      confirmarRegeneracion()
    }
  })
  // Guardar referencia para la confirmación (por si se usa fuera de didOpen)
  window.nuevosPuntosModal = nuevosPuntos
}

function confirmarRegeneracion() {
  // Limitar la búsqueda de inputs SOLO al modal de SweetAlert2
  const modalContainer = Swal.getHtmlContainer ? Swal.getHtmlContainer() : null;
  if (!modalContainer) {
    Swal.fire({
      title: "Error",
      text: "No se encontró el modal de edición. Intenta nuevamente.",
      icon: "error",
      confirmButtonColor: "#dc3545",
      customClass: { popup: "swal2-modal-custom" },
    });
    return;
  }

  // Buscar inputs solo dentro del modal
  const xInputs = modalContainer.querySelectorAll(".x-input");
  const fxInputs = modalContainer.querySelectorAll(".fx-input");
  const derivadaInputs = modalContainer.querySelectorAll(".derivada-input");

  if (xInputs.length === 0 || fxInputs.length === 0 || derivadaInputs.length === 0) {
    Swal.fire({
      title: "Error",
      text: "No se encontraron los campos de entrada. Intenta nuevamente.",
      icon: "error",
      confirmButtonColor: "#dc3545",
      customClass: { popup: "swal2-modal-custom" },
    });
    return;
  }

  let valid = true;
  const xs = [];
  const nuevosPuntos = [];

  // Recopilar todos los valores SOLO del modal
  for (let i = 0; i < xInputs.length; i++) {
    const xVal = Number.parseFloat(xInputs[i].value);
    const fxVal = Number.parseFloat(fxInputs[i].value);
    const dVal = Number.parseFloat(derivadaInputs[i].value);

    if (isNaN(xVal) || isNaN(fxVal) || isNaN(dVal)) {
      valid = false;
      break;
    }

    xs.push(xVal);
    nuevosPuntos.push([xVal, fxVal, dVal]);
  }

  // Validar que no haya x repetidos SOLO en el modal
  const xSet = new Set(xs);
  if (xSet.size !== xs.length) {
    valid = false;
  }

  if (!valid) {
    Swal.fire({
      title: "Error de validación",
      text: "Verifica que todos los valores sean numéricos y que no haya valores de x repetidos.",
      icon: "error",
      background: "#ffebee",
      confirmButtonColor: "#c62828",
      customClass: { popup: "swal2-modal-custom" },
    });
    return;
  }

  // Confirmar con SweetAlert2
  Swal.fire({
    title: '<span style="color:#1565c0;">¿Regenerar polinomio?</span>',
    text: "¿Deseas recalcular el polinomio con los nuevos puntos y derivadas?",
    icon: "question",
    background: "#e3f2fd",
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-sync-alt"></i> Sí, regenerar',
    cancelButtonText: '<i class="fas fa-times"></i> Cancelar',
    reverseButtons: true,
    customClass: {
      confirmButton: "swal2-confirm btn btn-success",
      cancelButton: "swal2-cancel btn btn-secondary",
      popup: "swal2-modal-custom",
    },
  }).then((result) => {
    if (result.isConfirmed) {
      // Crear formulario para enviar datos
      const form = document.createElement("form");
      form.method = "POST";
      form.style.display = "none";

      // CSRF token
      const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
      if (csrfTokenElement) {
        const csrfInput = document.createElement("input");
        csrfInput.type = "hidden";
        csrfInput.name = "csrfmiddlewaretoken";
        csrfInput.value = csrfTokenElement.value;
        form.appendChild(csrfInput);
      }

      // Puntos
      const puntosInput = document.createElement("input");
      puntosInput.type = "hidden";
      puntosInput.name = "puntos";
      puntosInput.value = nuevosPuntos.map((p) => `${p[0]},${p[1]},${p[2]}`).join(";");
      form.appendChild(puntosInput);

      // Punto de evaluación (mantener el actual)
      const xEvalElement = document.getElementById("x_eval");
      if (xEvalElement) {
        const xEvalInput = document.createElement("input");
        xEvalInput.type = "hidden";
        xEvalInput.name = "x_eval";
        xEvalInput.value = xEvalElement.value;
        form.appendChild(xEvalInput);
      }

      document.body.appendChild(form);
      form.submit();
    } else {
      Swal.fire({
        title: "Cancelado",
        text: "No se regeneró el polinomio.",
        icon: "info",
        background: "#e0e0e0",
        confirmButtonColor: "#1976d2",
        timer: 1500,
        showConfirmButton: false,
        customClass: { popup: "swal2-modal-custom" },
      });
    }
  });
}

function showGraphInstructions() {
  const instructions = document.getElementById("graph-instructions")
  if (instructions) {
    instructions.innerHTML = `
            <div class="alert alert-info ps-3 pt-1 pb-1 mb-1 text-dark">
                <h6><i class="fas fa-info-circle me-2"></i>Instrucciones de la gráfica interactiva:</h6>
                <ul class="mb-0 small">
                    <li><strong>Arrastrar puntos:</strong> Haz clic y arrastra los puntos verdes para cambiar su posición</li>
                    <li><strong>Zoom:</strong> Usa la rueda del mouse o los controles de zoom</li>
                    <li><strong>Pan:</strong> Arrastra el área de la gráfica para moverla</li>
                    <li><strong>Regenerar:</strong> Usa el botón "Regenerar Polinomio" para recalcular con las nuevas posiciones</li>
                    <li><strong>Reset:</strong> Usa el botón de reset para volver a la vista original</li>
                </ul>
                <div class="mt-2 text-center">
                  <button id="editar-puntos-btn" class="btn btn-success mt-4 p-1 " type="button">
                    <i class="fas fa-edit"></i> Editar puntos del problema
                  </button>
                </div>
            </div>
        `
    // Agregar event listener al botón
    const btn = document.getElementById("editar-puntos-btn")
    if (btn) {
      btn.addEventListener("click", () => {
        // Usar los puntos actuales de la gráfica
        if (window.datosGraficaHermite) {
          const puntos = window.datosGraficaHermite.puntos_x.map((x, i) => [
            x,
            window.datosGraficaHermite.puntos_y[i],
            window.datosGraficaHermite.derivadas[i]
          ])
          showRegenerateModal(puntos)
        }
      })
    }
  }
}

// Función para actualizar tema de la gráfica
function updateGraphTheme(isDark) {
  if (!currentPlot) return

  const update = {
    plot_bgcolor: isDark ? "#2d2d2d" : "#fafafa",
    paper_bgcolor: isDark ? "#1a1a1a" : "#ffffff",
    "font.color": isDark ? "#ffffff" : "#333333",
    "xaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "yaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "xaxis.zerolinecolor": isDark ? "#666666" : "#999999",
    "yaxis.zerolinecolor": isDark ? "#666666" : "#999999",
  }

  Plotly.relayout(currentPlot, update)
}

// Exportar funciones para uso global
window.initializeHermiteGraph = initializeHermiteGraph
window.updateGraphTheme = updateGraphTheme
window.confirmarRegeneracion = confirmarRegeneracion