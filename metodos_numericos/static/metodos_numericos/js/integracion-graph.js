// Configuración y funciones para gráficas de integración numérica con Plotly
let integrationPlot = null

function filterNumericPairs(xs, ys) {
  // Devuelve solo los pares donde ambos son números finitos
  const result = []
  for (let i = 0; i < xs.length; i++) {
    const x = xs[i]
    const y = ys[i]
    if (
      typeof x === 'number' && typeof y === 'number' &&
      isFinite(x) && isFinite(y)
    ) {
      result.push([x, y])
    }
  }
  return result
}

function initializeIntegrationGraph(datosGrafica) {
  if (!datosGrafica) return

  const graphDiv = document.getElementById("integration-graph")
  if (!graphDiv) return

  // Filtrar datos no numéricos para cada traza
  const curvaPairs = filterNumericPairs(datosGrafica.curva_x, datosGrafica.curva_y)
  const areaPairs = filterNumericPairs(datosGrafica.area_x, datosGrafica.area_y)
  const intervalosPairs = filterNumericPairs(datosGrafica.intervalos_x, datosGrafica.intervalos_y)

  // Configurar trazas
  const traces = [
    // Función original
    {
      x: curvaPairs.map(p => p[0]),
      y: curvaPairs.map(p => p[1]),
      type: "scatter",
      mode: "lines",
      name: "f(x)",
      line: {
        color: "#007bff",
        width: 3,
      },
      hovertemplate: "f(%{x:.3f}) = %{y:.3f}<extra></extra>",
    },
    // Área bajo la curva
    {
      x: areaPairs.map(p => p[0]),
      y: areaPairs.map(p => p[1]),
      type: "scatter",
      mode: "lines",
      fill: "tozeroy",
      fillcolor: "rgba(0, 123, 255, 0.3)",
      line: { color: "rgba(0, 123, 255, 0)" },
      name: "Área de integración",
      hoverinfo: "skip",
      showlegend: true,
    },
    // Puntos de los intervalos
    {
      x: intervalosPairs.map(p => p[0]),
      y: intervalosPairs.map(p => p[1]),
      type: "scatter",
      mode: "markers",
      name: "Puntos de evaluación",
      marker: {
        color: "#28a745",
        size: 8,
        symbol: "circle",
        line: {
          color: "#ffffff",
          width: 1,
        },
      },
      hovertemplate: "x=%{x:.3f}<br>f(x)=%{y:.3f}<extra></extra>",
    },
  ]

  // Agregar aproximación según el método
  if (datosGrafica.metodo === "trapecio" && Array.isArray(datosGrafica.trapecio_x) && datosGrafica.trapecio_x.length > 0) {
    const trapecioPairs = filterNumericPairs(datosGrafica.trapecio_x, datosGrafica.trapecio_y)
    traces.push({
      x: trapecioPairs.map(p => p[0]),
      y: trapecioPairs.map(p => p[1]),
      type: "scatter",
      mode: "lines",
      fill: "toself",
      fillcolor: "rgba(255, 193, 7, 0.4)",
      line: {
        color: "#ffc107",
        width: 2,
      },
      name: "Aproximación trapezoidal",
      hoverinfo: "skip",
    })
  }

  // Líneas verticales para los límites de integración
  const curvaY = curvaPairs.map(p => p[1])
  const yRange = [
    Math.min(...curvaY, 0) - 1,
    Math.max(...curvaY, 0) + 1
  ]

  traces.push(
    // Línea en x = a
    {
      x: [datosGrafica.a, datosGrafica.a],
      y: yRange,
      type: "scatter",
      mode: "lines",
      line: {
        color: "#dc3545",
        width: 2,
        dash: "dash",
      },
      name: `x = ${datosGrafica.a}`,
      hoverinfo: "skip",
    },
    // Línea en x = b
    {
      x: [datosGrafica.b, datosGrafica.b],
      y: yRange,
      type: "scatter",
      mode: "lines",
      line: {
        color: "#dc3545",
        width: 2,
        dash: "dash",
      },
      name: `x = ${datosGrafica.b}`,
      hoverinfo: "skip",
    },
  )

  // Configuración del layout
  const layout = {
    title: {
      text: `Integración Numérica - ${datosGrafica.metodo.charAt(0).toUpperCase() + datosGrafica.metodo.slice(1)}`,
      font: { size: 16, color: "#333" },
    },
    xaxis: {
      title: "x",
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
    },
    yaxis: {
      title: "f(x)",
      gridcolor: "#e0e0e0",
      zeroline: true,
      zerolinecolor: "#999",
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
    hovermode: "closest",
    margin: { t: 80, r: 50, b: 50, l: 50 },
    annotations: [
      {
        x: (datosGrafica.a + datosGrafica.b) / 2,
        y: Math.max(...datosGrafica.curva_y) * 0.8,
        text: `∫ f(x)dx ≈ ${datosGrafica.resultado.toFixed(6)}<br>n = ${datosGrafica.n}, h = ${datosGrafica.h.toFixed(4)}`,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 2,
        arrowcolor: "#333",
        ax: 0,
        ay: -30,
        bgcolor: "rgba(255,255,255,0.9)",
        bordercolor: "#333",
        borderwidth: 1,
        font: { size: 12, color: "#333" },
      },
    ],
  }

  // Configuración
  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d"],
    responsive: true,
  }

  // Crear gráfica
  Plotly.newPlot(graphDiv, traces, layout, config)
  integrationPlot = graphDiv

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

  // Mostrar información adicional
  showIntegrationInfo(datosGrafica)
}

function showIntegrationInfo(datosGrafica) {
  const infoDiv = document.getElementById("integration-info")
  if (infoDiv) {
    const metodosInfo = {
      trapecio: {
        nombre: "Regla del Trapecio",
        descripcion: "Aproxima el área usando trapecios",
        formula: "∫f(x)dx ≈ (h/2)[f(x₀) + 2∑f(xᵢ) + f(xₙ)]",
      },
      simpson13: {
        nombre: "Regla de Simpson 1/3",
        descripcion: "Aproxima usando parábolas (n debe ser par)",
        formula: "∫f(x)dx ≈ (h/3)[f(x₀) + 4∑f(x₂ᵢ₋₁) + 2∑f(x₂ᵢ) + f(xₙ)]",
      },
      simpson38: {
        nombre: "Regla de Simpson 3/8",
        descripcion: "Aproxima usando cúbicas (n debe ser múltiplo de 3)",
        formula: "∫f(x)dx ≈ (3h/8)[f(x₀) + 3∑f(x₃ᵢ₋₂) + 3∑f(x₃ᵢ₋₁) + 2∑f(x₃ᵢ) + f(xₙ)]",
      },
    }

    const info = metodosInfo[datosGrafica.metodo] || metodosInfo["trapecio"]

    infoDiv.innerHTML = `
            <div class="alert alert-info ps-3 pt-1 pb-2 text-dark">
                <h6><i class="fas fa-info-circle me-2"></i>${info.nombre}</h6>
                <p class="mb-2">${info.descripcion}</p>
                <div class="small">
                    <strong>Fórmula:</strong> <code>${info.formula}</code><br>
                    <strong>Intervalo:</strong> [${datosGrafica.a}, ${datosGrafica.b}]<br>
                    <strong>Subintervalos:</strong> ${datosGrafica.n}<br>
                    <strong>Ancho (h):</strong> ${datosGrafica.h.toFixed(6)}<br>
                    <strong>Resultado:</strong> ${datosGrafica.resultado.toFixed(8)}
                </div>
            </div>
        `
  }
}

// Función para actualizar tema de la gráfica de integración
function updateIntegrationGraphTheme(isDark) {
  if (!integrationPlot) return

  const update = {
    plot_bgcolor: isDark ? "#2d2d2d" : "#fafafa",
    paper_bgcolor: isDark ? "#1a1a1a" : "#ffffff",
    "font.color": isDark ? "#ffffff" : "#333333",
    "xaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "yaxis.gridcolor": isDark ? "#444444" : "#e0e0e0",
    "xaxis.zerolinecolor": isDark ? "#666666" : "#999999",
    "yaxis.zerolinecolor": isDark ? "#666666" : "#999999",
  }

  Plotly.relayout(integrationPlot, update)
}

// Exportar funciones para uso global
window.initializeIntegrationGraph = initializeIntegrationGraph
window.updateIntegrationGraphTheme = updateIntegrationGraphTheme
