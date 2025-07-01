// Configuración y funciones para gráficas de Simplex con Plotly
let currentSimplexPlot = null
const Plotly = window.Plotly // Declare Plotly variable
const Swal = window.Swal // Declare Swal variable

function initializeSimplexGraph(datosGrafica) {
  if (!datosGrafica) return

  const graphDiv = document.getElementById("simplex-graph")
  if (!graphDiv) return

  // Configurar trazas
  const traces = []

  // 1. Área factible (polígono sombreado)
  if (datosGrafica.vertices_factibles && datosGrafica.vertices_factibles.length > 2) {
    const vertices = datosGrafica.vertices_factibles
    const x_vertices = vertices.map((v) => v[0])
    const y_vertices = vertices.map((v) => v[1])

    // Cerrar el polígono
    x_vertices.push(vertices[0][0])
    y_vertices.push(vertices[0][1])

    traces.push({
      x: x_vertices,
      y: y_vertices,
      fill: "toself",
      fillcolor: "rgba(144, 238, 144, 0.3)",
      line: {
        color: "rgba(34, 139, 34, 0.8)",
        width: 2,
        dash: "dot",
      },
      mode: "lines",
      name: "Región Factible",
      hovertemplate: "Región Factible<extra></extra>",
      showlegend: true,
    })
  }

  // 2. Líneas de restricciones
  datosGrafica.restricciones.forEach((restriccion, index) => {
    const colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
    const color = colors[index % colors.length]

    traces.push({
      x: restriccion.x,
      y: restriccion.y,
      type: "scatter",
      mode: "lines",
      name: restriccion.nombre,
      line: {
        color: color,
        width: 3,
      },
      hovertemplate: `${restriccion.nombre}<br>x₁=%{x:.3f}, x₂=%{y:.3f}<extra></extra>`,
    })
  })

  // 3. Líneas de la función objetivo
  // Solo mostrar la línea óptima (es_optimo) y no las demás líneas Z auxiliares
  datosGrafica.objetivo_lines.forEach((objLine, index) => {
    if (!objLine.es_optimo) return // Solo graficar la óptima
    traces.push({
      x: objLine.x,
      y: objLine.y,
      type: "scatter",
      mode: "lines",
      name: `Función Objetivo Óptima (Z=${objLine.z.toFixed(2)})`,
      line: {
        color: "#FF1744",
        width: 4,
        dash: "solid",
      },
      hovertemplate: `Z = ${objLine.z.toFixed(3)}<br>x₁=%{x:.3f}, x₂=%{y:.3f}<extra></extra>`,
      showlegend: true,
    })
  })

  // 4. Vértices de la región factible
  if (datosGrafica.vertices_factibles && datosGrafica.vertices_factibles.length > 0) {
    const vertices = datosGrafica.vertices_factibles
    traces.push({
      x: vertices.map((v) => v[0]),
      y: vertices.map((v) => v[1]),
      type: "scatter",
      mode: "markers+text",
      name: "Vértices Factibles",
      marker: {
        color: "#2E7D32",
        size: 8,
        symbol: "circle",
        line: {
          color: "#FFFFFF",
          width: 2,
        },
      },
      text: vertices.map((v, i) => `V${i + 1}(${v[0].toFixed(2)}, ${v[1].toFixed(2)})`),
      textposition: "top center",
      textfont: {
        size: 9,
        color: "#2E7D32",
      },
      hovertemplate: "Vértice: (%{x:.3f}, %{y:.3f})<extra></extra>",
    })
  }

  // 5. Punto óptimo
  if (datosGrafica.punto_optimo && datosGrafica.punto_optimo.x !== undefined) {
    traces.push({
      x: [datosGrafica.punto_optimo.x],
      y: [datosGrafica.punto_optimo.y],
      type: "scatter",
      mode: "markers+text",
      name: "Punto Óptimo",
      marker: {
        color: "#D32F2F",
        size: 15,
        symbol: "star",
        line: {
          color: "#FFFFFF",
          width: 3,
        },
      },
      text: [
        `ÓPTIMO<br>(${datosGrafica.punto_optimo.x.toFixed(3)}, ${datosGrafica.punto_optimo.y.toFixed(3)})<br>Z=${datosGrafica.punto_optimo.z.toFixed(3)}`,
      ],
      textposition: "top center",
      textfont: {
        size: 11,
        color: "#D32F2F",
        family: "Arial Black",
      },
      hovertemplate: `Punto Óptimo<br>x₁=%{x:.6f}<br>x₂=%{y:.6f}<br>Z=${datosGrafica.punto_optimo.z.toFixed(6)}<extra></extra>`,
    })
  }

  // Configuración del layout optimizada para responsive
  const layout = {
    title: {
      text: `Método Simplex - Gráfica de Programación Lineal<br><sub>Función Objetivo: ${datosGrafica.tipo_optimizacion} Z = ${datosGrafica.funcion_objetivo.ecuacion}</sub>`,
      font: { size: 16, color: "#333" },
    },
    xaxis: {
      title: `${datosGrafica.nombres_variables[0]} (Variable 1)`,
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
      range: [0, datosGrafica.rango.x_max],
      constrain: "domain",
    },
    yaxis: {
      title: `${datosGrafica.nombres_variables[1]} (Variable 2)`,
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
      range: [0, datosGrafica.rango.y_max],
      scaleanchor: "x",
      scaleratio: 1,
    },
    plot_bgcolor: "#fafafa",
    paper_bgcolor: "#ffffff",
    showlegend: true,
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: "rgba(255,255,255,0.9)",
      bordercolor: "#ccc",
      borderwidth: 1,
      font: { size: 10 },
    },
    dragmode: "pan",
    hovermode: "closest",
    margin: { t: 80, r: 50, b: 60, l: 60 },
    autosize: true,
  }

  // Configuración optimizada
  const config = {
    displayModeBar: true,
    modeBarButtonsToAdd: [
      {
        name: "Información del problema",
        icon: {
          width: 857.1,
          height: 1000,
          path: "M428.6 857.1c236.3 0 428.6-192.2 428.6-428.6S664.9 0 428.6 0 0 192.2 0 428.6s192.2 428.5 428.6 428.5zM428.6 114.3c173.1 0 314.3 141.1 314.3 314.3S601.7 742.9 428.6 742.9 114.3 601.7 114.3 428.6s141.1-314.3 314.3-314.3zM457.1 285.7c0-15.8-12.8-28.6-28.6-28.6s-28.6 12.8-28.6 28.6v285.7c0 15.8 12.8 28.6 28.6 28.6s28.6-12.8 28.6-28.6V285.7zM428.6 657.1c15.8 0 28.6-12.8 28.6-28.6s-12.8-28.6-28.6-28.6-28.6 12.8-28.6 28.6 12.8 28.6 28.6 28.6z",
        },
        click: () => {
          showSimplexInfo(datosGrafica)
        },
      },
    ],
    modeBarButtonsToRemove: ["select2d", "lasso2d"],
    responsive: true,
  }

  // Crear gráfica con configuración responsive
  Plotly.newPlot(graphDiv, traces, layout, config)
  currentSimplexPlot = graphDiv

  // Forzar resize tras renderizado inicial
  setTimeout(() => {
    if (graphDiv && Plotly) {
      Plotly.Plots.resize(graphDiv)
    }
  }, 100)

  // Ajuste automático con ResizeObserver (igual que Hermite)
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(() => {
      if (graphDiv && Plotly) {
        Plotly.Plots.resize(graphDiv)
      }
    })
    ro.observe(graphDiv)
  } else {
    // Fallback: ajustar al redimensionar ventana
    window.addEventListener("resize", () => {
      if (graphDiv && Plotly) {
        Plotly.Plots.resize(graphDiv)
      }
    })
  }

  // Mostrar instrucciones
  showSimplexGraphInstructions()

  // Detectar tema desde localStorage (key: theme, value: 'dark' o 'light')
  let theme = null
  try {
    theme = localStorage.getItem('theme')
  } catch (e) {}
  if (theme === 'dark') {
    setTimeout(() => updateSimplexGraphTheme(true), 150)
  } else if (theme === 'light') {
    setTimeout(() => updateSimplexGraphTheme(false), 150)
  }
}

function showSimplexInfo(datosGrafica) {
  // Validar que Swal esté disponible
  if (typeof Swal === "undefined" || !Swal || typeof Swal.fire !== "function") {
    alert("No se pudo mostrar la información: SweetAlert2 no está disponible.")
    return
  }
  if (!datosGrafica) {
    Swal.fire({
      icon: "error",
      title: "Sin datos",
      text: "No hay información para mostrar.",
      customClass: { popup: "swal2-modal-custom" },
    })
    return
  }
  const restrictionsHtml = (datosGrafica.restricciones || [])
    .map((r, i) => `<li><strong>Restricción ${i + 1}:</strong> ${r.nombre}</li>`)
    .join("")

  const verticesHtml = (datosGrafica.vertices_factibles || [])
    .map((v, i) => `<li><strong>V${i + 1}:</strong> (${v[0]?.toFixed(3) ?? "-"}, ${v[1]?.toFixed(3) ?? "-"})</li>`)
    .join("")

  Swal.fire({
    title: '<span style="color:#1565c0;font-weight:bold;">Información del Problema</span>',
    html: `
      <div class="text-start" style="max-width: 100vw; overflow-x: auto;">
        <div class="groups" style="background:rgba(255,255,255,0.97); box-shadow:0 2px 12px rgba(0,0,0,0.08); border-radius:10px; padding:10px 18px; margin-bottom:0; min-width:320px; max-width:540px;">
          <h6 class="text-primary">Función Objetivo:</h6>
          <p><strong>${datosGrafica.tipo_optimizacion || ""}:</strong> Z = ${datosGrafica.funcion_objetivo?.ecuacion || "-"}</p>
          <h6 class="text-primary">Restricciones:</h6>
          <ul style="font-size:0.97em;">${restrictionsHtml}</ul>
          <h6 class="text-primary">Vértices de la Región Factible:</h6>
          <ul style="font-size:0.97em;">${verticesHtml}</ul>
          <h6 class="text-primary">Punto Óptimo:</h6>
          <p><strong>${datosGrafica.nombres_variables?.[0] || "x₁"} = ${datosGrafica.punto_optimo?.x !== undefined ? datosGrafica.punto_optimo.x.toFixed(6) : "-"}</strong></p>
          <p><strong>${datosGrafica.nombres_variables?.[1] || "x₂"} = ${datosGrafica.punto_optimo?.y !== undefined ? datosGrafica.punto_optimo.y.toFixed(6) : "-"}</strong></p>
          <p><strong>Valor Óptimo: Z = ${datosGrafica.punto_optimo?.z !== undefined ? datosGrafica.punto_optimo.z.toFixed(6) : "-"}</strong></p>
        </div>
      </div>
    `,
    icon: "info",
    confirmButtonText: "Cerrar",
    customClass: {
      popup: "swal2-modal-custom",
      confirmButton: "btn btn-primary",
    },
    width: "600px",
    didOpen: () => {
      // Forzar z-index alto para el modal y el fondo
      const swalPopup = document.querySelector(".swal2-container")
      if (swalPopup) {
        swalPopup.style.zIndex = "3000"
      }
    },
  })
}

function showSimplexGraphInstructions() {
  const instructions = document.getElementById("simplex-graph-instructions")
  if (instructions) {
    instructions.innerHTML = `
      <div class="alert text-dark bg-light alert-info ps-3 pt-2 pb-2 mb-2">
        <h6><i class="fas fa-info-circle me-2"></i>Interpretación de la gráfica:</h6>
        <ul class="mb-2 small">
          <li><strong>Área Verde:</strong> Región factible donde se cumplen todas las restricciones</li>
          <li><strong>Líneas de Colores:</strong> Cada restricción del problema</li>
          <li><strong>Líneas Rojas:</strong> Función objetivo (la sólida es la óptima)</li>
          <li><strong>Puntos Verdes:</strong> Vértices de la región factible</li>
          <li><strong>Estrella Roja:</strong> Punto óptimo encontrado por Simplex</li>
        </ul>
        <div class="mt-2 text-center">
          <small class="text-muted">
            <i class="fas fa-lightbulb me-1"></i>
            El método Simplex encuentra el óptimo evaluando los vértices de la región factible
          </small>
        </div>
        <div class="mt-2 text-center">
          <button id="info-problema-btn" class="btn btn-info btn-sm" type="button">
            <i class="fas fa-info-circle"></i> Ver información del problema
          </button>
        </div>
      </div>
    `

    // Agregar event listener al botón
    const btn = document.getElementById("info-problema-btn")
    if (btn) {
      btn.addEventListener("click", () => {
        if (window.datosGraficaSimplex) {
          showSimplexInfo(window.datosGraficaSimplex)
        }
      })
    }
  }
}

// Función para actualizar tema de la gráfica
function updateSimplexGraphTheme(isDark) {
  if (!currentSimplexPlot) return

  const update = {
    plot_bgcolor: isDark ? "#2d2d2d" : "#fafafa",
    paper_bgcolor: isDark ? "#1a1a1a" : "#ffffff",
    "font.color": isDark ? "#ffffff" : "#333333",
    "xaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "yaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "xaxis.zerolinecolor": isDark ? "#666666" : "#999999",
    "yaxis.zerolinecolor": isDark ? "#666666" : "#999999",
    // Cambiar color de fondo de la leyenda
    "legend.bgcolor": isDark ? "#23272e" : "rgba(255,255,255,0.9)",
    "legend.bordercolor": isDark ? "#444" : "#ccc",
    // Cambiar color del título
    "title.font.color": isDark ? "#fff" : "#333",
  }

  Plotly.relayout(currentSimplexPlot, update)

  // Cambiar fondo de los labels de la leyenda (SVG)
  const graphDiv = currentSimplexPlot
  if (graphDiv) {
    const legend = graphDiv.querySelector('.legend')
    if (legend) {
      legend.style.background = isDark ? '#23272e' : 'rgba(255,255,255,0.9)'
      legend.style.color = isDark ? '#fff' : '#222'
      // Cambiar fondo de los labels
      const labels = legend.querySelectorAll('g.traces text')
      labels.forEach(label => {
        label.style.fill = isDark ? '#fff' : '#222'
      })
    }
    // Forzar color del título en SVG
    const title = graphDiv.querySelector('.gtitle')
    if (title) {
      title.style.fill = isDark ? '#fff' : '#333'
    }
  }
}

// Exportar funciones para uso global
window.initializeSimplexGraph = initializeSimplexGraph
window.updateSimplexGraphTheme = updateSimplexGraphTheme