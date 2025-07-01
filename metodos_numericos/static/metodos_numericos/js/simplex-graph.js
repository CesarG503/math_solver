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
  datosGrafica.objetivo_lines.forEach((objLine, index) => {
    const isOptimal = objLine.es_optimo
    traces.push({
      x: objLine.x,
      y: objLine.y,
      type: "scatter",
      mode: "lines",
      name: isOptimal
        ? `Función Objetivo Óptima (Z=${objLine.z.toFixed(2)})`
        : `Función Objetivo (Z=${objLine.z.toFixed(2)})`,
      line: {
        color: isOptimal ? "#FF1744" : "#FF8A65",
        width: isOptimal ? 4 : 2,
        dash: isOptimal ? "solid" : "dash",
      },
      hovertemplate: `Z = ${objLine.z.toFixed(3)}<br>x₁=%{x:.3f}, x₂=%{y:.3f}<extra></extra>`,
      showlegend: isOptimal,
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

  // Configuración del layout
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
      x: 1.02,
      y: 1,
      bgcolor: "rgba(255,255,255,0.9)",
      bordercolor: "#ccc",
      borderwidth: 1,
      font: { size: 10 },
    },
    dragmode: "pan",
    hovermode: "closest",
    margin: { t: 80, r: 150, b: 60, l: 60 },
    annotations: [
      {
        x: datosGrafica.rango.x_max * 0.02,
        y: datosGrafica.rango.y_max * 0.95,
        text: `<b>Región Factible:</b><br>Área sombreada en verde<br><b>Restricciones:</b><br>Líneas de colores<br><b>Función Objetivo:</b><br>Líneas rojas`,
        showarrow: false,
        align: "left",
        bgcolor: "rgba(255,255,255,0.8)",
        bordercolor: "#ccc",
        borderwidth: 1,
        font: { size: 9 },
      },
    ],
  }

  // Configuración
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

  // Crear gráfica
  Plotly.newPlot(graphDiv, traces, layout, config)
  currentSimplexPlot = graphDiv

  // Forzar resize tras renderizado inicial
  setTimeout(() => {
    if (graphDiv && Plotly) {
      Plotly.Plots.resize(graphDiv)
    }
  }, 100)

  // Ajuste automático con ResizeObserver
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
}

function showSimplexInfo(datosGrafica) {
  const restrictionsHtml = datosGrafica.restricciones
    .map((r, i) => `<li><strong>Restricción ${i + 1}:</strong> ${r.nombre}</li>`)
    .join("")

  const verticesHtml = datosGrafica.vertices_factibles
    .map((v, i) => `<li><strong>V${i + 1}:</strong> (${v[0].toFixed(3)}, ${v[1].toFixed(3)})</li>`)
    .join("")

  Swal.fire({
    title: '<span style="color:#1565c0;font-weight:bold;">Información del Problema</span>',
    html: `
            <div class="text-start">
                <h6 class="text-primary">Función Objetivo:</h6>
                <p><strong>${datosGrafica.tipo_optimizacion}:</strong> Z = ${datosGrafica.funcion_objetivo.ecuacion}</p>
                
                <h6 class="text-primary">Restricciones:</h6>
                <ul class="small">${restrictionsHtml}</ul>
                
                <h6 class="text-primary">Vértices de la Región Factible:</h6>
                <ul class="small">${verticesHtml}</ul>
                
                <h6 class="text-primary">Punto Óptimo:</h6>
                <p><strong>${datosGrafica.nombres_variables[0]} = ${datosGrafica.punto_optimo.x.toFixed(6)}</strong></p>
                <p><strong>${datosGrafica.nombres_variables[1]} = ${datosGrafica.punto_optimo.y.toFixed(6)}</strong></p>
                <p><strong>Valor Óptimo: Z = ${datosGrafica.punto_optimo.z.toFixed(6)}</strong></p>
            </div>
        `,
    icon: "info",
    confirmButtonText: "Cerrar",
    customClass: {
      popup: "swal2-modal-custom",
      confirmButton: "btn btn-primary",
    },
    width: "600px",
  })
}

function showSimplexGraphInstructions() {
  const instructions = document.getElementById("simplex-graph-instructions")
  if (instructions) {
    instructions.innerHTML = `
            <div class="alert alert-info ps-3 pt-2 pb-2 mb-2 text-dark">
                <h6><i class="fas fa-info-circle me-2"></i>Interpretación de la gráfica:</h6>
                <ul class="mb-2 small">
                    <li><strong>Área Verde:</strong> Región factible donde se cumplen todas las restricciones</li>
                    <li><strong>Líneas de Colores:</strong> Cada restricción del problema</li>
                    <li><strong>Líneas Rojas:</strong> Función objetivo (la sólida es la óptima)</li>
                    <li><strong>Puntos Verdes:</strong> Vértices de la región factible</li>
                    <li><strong>Estrella Roja:</strong> Punto óptimo encontrado por Simplex</li>
                </ul>
                <div class="text-center">
                    <small class="text-muted">
                        <i class="fas fa-lightbulb me-1"></i>
                        El método Simplex encuentra el óptimo evaluando los vértices de la región factible
                    </small>
                </div>
            </div>
        `
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
  }

  Plotly.relayout(currentSimplexPlot, update)
}

// Exportar funciones para uso global
window.initializeSimplexGraph = initializeSimplexGraph
window.updateSimplexGraphTheme = updateSimplexGraphTheme
