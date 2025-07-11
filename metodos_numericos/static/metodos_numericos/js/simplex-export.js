// Funciones para exportar resultados del método Simplex

function exportarAPDF() {
    // Requiere jsPDF y jsPDF-AutoTable
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'pt', 'a4');
    const margin = 40;
    let y = margin;
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const lineSpacing = 18; // Espaciado estándar entre líneas
    // Título principal
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(20);
    doc.setTextColor(0, 102, 204);
    doc.text('Método Simplex - Solución Óptima', pageWidth / 2, y, { align: 'center' });
    y += 30;
    // Fecha
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    doc.text(`Fecha: ${new Date().toLocaleDateString()}`, pageWidth - margin, y, { align: 'right' });
    y += 20;
    // Problema original
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 102, 204);
    doc.text('Problema Original', margin, y);
    y += lineSpacing;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    // Función objetivo
    const tipoOptimizacion = document.querySelector('input[name="tipo_optimizacion"]:checked')?.value || 'maximizar';
    const funcionObjetivo = obtenerFuncionObjetivo();
    y = addWrappedText(doc, `${tipoOptimizacion.charAt(0).toUpperCase() + tipoOptimizacion.slice(1)}: Z = ${funcionObjetivo}`, margin, y, pageWidth - 2 * margin);
    // Restricciones
    y += 4;
    doc.text('Sujeto a:', margin, y);
    y += 12;
    const restricciones = obtenerRestricciones();
    restricciones.forEach(r => {
        y = addWrappedText(doc, `  ${r}`, margin + 10, y, pageWidth - 2 * margin - 10);
    });
    y += 8;
    // Solución óptima
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(40, 167, 69);
    doc.text('Solución Óptima', margin, y);
    y += lineSpacing;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    // Variables solución
    const solucionElement = document.querySelector('.alert-success');
    if (solucionElement) {
        const variables = solucionElement.querySelectorAll('.col-md-6 strong');
        variables.forEach(variable => {
            y = addWrappedText(doc, variable.textContent, margin, y, pageWidth - 2 * margin);
        });
        y += 2;
        // Valor óptimo
        const valorOptimo = document.querySelector('#valor-optimo');
        if (valorOptimo) {
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(40, 167, 69);
            y = addWrappedText(doc, valorOptimo.textContent.replace(/[^ 0-\uFFFF\w\s=.:,-]/g, ''), margin, y, pageWidth - 2 * margin);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(0, 0, 0);
        }
    }
    y += 8;
    // Método utilizado
    const metodoElement = document.querySelector('.metodo-indicator');
    if (metodoElement) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(0, 102, 204);
        doc.text('Método Utilizado:', margin, y);
        y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(0, 0, 0);
        y = addWrappedText(doc, metodoElement.textContent.trim(), margin, y, pageWidth - 2 * margin);
    }
    y += 8;
    // Proceso Simplex Paso a Paso
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 102, 204);
    doc.text('Proceso Simplex Paso a Paso', margin, y);
    y += lineSpacing;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    const pasosContainer = document.querySelector('.solution-steps');
    if (pasosContainer) {
        const pasos = pasosContainer.childNodes;
        pasos.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (["H3", "H4", "H5"].includes(node.tagName)) {
                    doc.setFont('helvetica', 'bold');
                    doc.setTextColor(0, 102, 204);
                    y = addWrappedText(doc, node.textContent, margin, y, pageWidth - 2 * margin);
                    doc.setFont('helvetica', 'normal');
                    doc.setTextColor(0, 0, 0);
                } else if (node.tagName === 'P') {
                    y = addWrappedText(doc, node.textContent, margin, y, pageWidth - 2 * margin);
                } else if (node.tagName === 'DIV' && node.classList.contains('simplex-table-container')) {
                    const tabla = node.querySelector('table');
                    if (tabla && window.jspdf && window.jspdf.autoTable) {
                        window.jspdf.autoTable(doc, {
                            html: tabla,
                            startY: y,
                            margin: { left: margin, right: margin },
                            styles: {
                                fontSize: 10,
                                cellPadding: 2,
                                halign: 'center',
                                valign: 'middle',
                                textColor: [0,0,0],
                                lineColor: [0,102,204],
                                lineWidth: 0.2
                            },
                            headStyles: {
                                fillColor: [0,102,204],
                                textColor: [255,255,255],
                                fontStyle: 'bold',
                                halign: 'center',
                                valign: 'middle',
                                fontSize: 11
                            },
                            alternateRowStyles: {
                                fillColor: [231,243,255]
                            },
                            tableLineColor: [0,102,204],
                            tableLineWidth: 0.2
                        });
                        y = doc.lastAutoTable.finalY + 12;
                    } else if (tabla) {
                        y = addWrappedText(doc, '[Tabla no exportada: jsPDF-AutoTable no cargado]', margin, y, pageWidth - 2 * margin);
                    }
                } else if (node.tagName === 'TABLE') {
                    if (window.jspdf && window.jspdf.autoTable) {
                        window.jspdf.autoTable(doc, {
                            html: node,
                            startY: y,
                            margin: { left: margin, right: margin },
                            styles: {
                                fontSize: 10,
                                cellPadding: 2,
                                halign: 'center',
                                valign: 'middle',
                                textColor: [0,0,0],
                                lineColor: [0,102,204],
                                lineWidth: 0.2
                            },
                            headStyles: {
                                fillColor: [0,102,204],
                                textColor: [255,255,255],
                                fontStyle: 'bold',
                                halign: 'center',
                                valign: 'middle',
                                fontSize: 11
                            },
                            alternateRowStyles: {
                                fillColor: [231,243,255]
                            },
                            tableLineColor: [0,102,204],
                            tableLineWidth: 0.2
                        });
                        y = doc.lastAutoTable.finalY + 12;
                    } else {
                        y = addWrappedText(doc, '[Tabla no exportada: jsPDF-AutoTable no cargado]', margin, y, pageWidth - 2 * margin);
                    }
                } else if (node.tagName === 'DIV') {
                    y = addWrappedText(doc, node.textContent, margin, y, pageWidth - 2 * margin);
                }
                if (y > pageHeight - margin - 30) {
                    doc.addPage();
                    y = margin;
                }
            }
        });
    }
    doc.save('simplex-solucion.pdf');
    Swal.fire({
        icon: 'success',
        title: '¡Exportado!',
        text: 'El archivo PDF se ha descargado correctamente.',
        timer: 2000,
        showConfirmButton: false
    });
}

// Utilidad para salto de línea automático
function addWrappedText(doc, text, x, y, maxWidth) {
    const lines = doc.splitTextToSize(text, maxWidth);
    lines.forEach(line => {
        doc.text(line, x, y);
        y += 14;
    });
    return y;
}

function exportarAWord() {
    // Crear contenido HTML para Word
    let htmlContent = `
        <html>
        <head>
            <meta charset="utf-8">
            <title>Método Simplex - Solución</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #0066cc; text-align: center; }
                h2 { color: #0066cc; border-bottom: 2px solid #0066cc; }
                h3 { color: #666; }
                .solucion { background-color: #d4edda; padding: 15px; border-radius: 5px; }
                .variable { margin: 5px 0; font-weight: bold; }
                .valor-optimo { text-align: center; font-size: 18px; color: #28a745; font-weight: bold; }
                .metodo { background-color: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
                table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Método Simplex - Solución Óptima</h1>
            <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
            
            <h2>Problema Original</h2>
    `;
    
    // Agregar problema original
    const tipoOptimizacion = document.querySelector('input[name="tipo_optimizacion"]:checked')?.value || 'maximizar';
    const funcionObjetivo = obtenerFuncionObjetivo();
    const restricciones = obtenerRestricciones();
    
    htmlContent += `
        <p><strong>${tipoOptimizacion.charAt(0).toUpperCase() + tipoOptimizacion.slice(1)}:</strong> Z = ${funcionObjetivo}</p>
        <p><strong>Sujeto a:</strong></p>
        <ul>
    `;
    
    restricciones.forEach(restriccion => {
        htmlContent += `<li>${restriccion}</li>`;
    });
    
    htmlContent += `</ul>`;
    
    // Agregar solución
    htmlContent += `<h2>Solución Óptima</h2><div class="solucion">`;
    
    const solucionElement = document.querySelector('.alert-success');
    if (solucionElement) {
        const variables = solucionElement.querySelectorAll('.col-md-6 strong');
        variables.forEach(variable => {
            htmlContent += `<div class="variable">${variable.textContent}</div>`;
        });
        
        const valorOptimo = document.querySelector('#valor-optimo');
        if (valorOptimo) {
            htmlContent += `<div class="valor-optimo">${valorOptimo.textContent.replace(/[^\w\s=.:,-]/g, '')}</div>`;
        }
    }
    
    htmlContent += `</div>`;
    
    // Método utilizado
    const metodoElement = document.querySelector('.metodo-indicator');
    if (metodoElement) {
        htmlContent += `
            <div class="metodo">
                <h3>Método Utilizado</h3>
                <p>${metodoElement.textContent.trim()}</p>
            </div>
        `;
    }
    
    // Proceso Simplex Paso a Paso
    htmlContent += `<h2>Proceso Simplex Paso a Paso</h2>`;
    const pasosContainer = document.querySelector('.solution-steps');
    if (pasosContainer) {
        pasosContainer.childNodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (['H3', 'H4', 'H5'].includes(node.tagName)) {
                    htmlContent += `<${node.tagName.toLowerCase()} style="color:#0066cc;">${node.textContent}</${node.tagName.toLowerCase()}>`;
                } else if (node.tagName === 'DIV' && node.classList.contains('simplex-table-container')) {
                    htmlContent += node.innerHTML;
                } else if (node.tagName === 'TABLE') {
                    htmlContent += node.outerHTML;
                } else if (node.tagName === 'DIV') {
                    htmlContent += `<div>${node.textContent}</div>`;
                }
            }
        });
    }
    htmlContent += `</body></html>`;
    
    // Crear y descargar archivo
    const blob = new Blob([htmlContent], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'simplex-solucion.doc';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Mostrar mensaje de éxito
    Swal.fire({
        icon: 'success',
        title: '¡Exportado!',
        text: 'El archivo Word se ha descargado correctamente.',
        timer: 2000,
        showConfirmButton: false
    });
}

function exportarAExcel() {
    // Crear libro de trabajo
    const wb = XLSX.utils.book_new();
    const hojaNombres = new Set(); // Para evitar nombres duplicados

    // Hoja 1: Problema Original
    const problemaData = [];
    const tipoOptimizacion = document.querySelector('input[name="tipo_optimizacion"]:checked')?.value || 'maximizar';
    const funcionObjetivo = obtenerFuncionObjetivo();
    const restricciones = obtenerRestricciones();

    problemaData.push(['MÉTODO SIMPLEX - SOLUCIÓN ÓPTIMA']);
    problemaData.push(['Fecha:', new Date().toLocaleDateString()]);
    problemaData.push([]);
    problemaData.push(['PROBLEMA ORIGINAL']);
    problemaData.push(['Tipo:', tipoOptimizacion.charAt(0).toUpperCase() + tipoOptimizacion.slice(1)]);
    problemaData.push(['Función Objetivo:', `Z = ${funcionObjetivo}`]);
    problemaData.push([]);
    problemaData.push(['RESTRICCIONES']);

    restricciones.forEach((restriccion, index) => {
        problemaData.push([`Restricción ${index + 1}:`, restriccion]);
    });

    const ws1 = XLSX.utils.aoa_to_sheet(problemaData);
    XLSX.utils.book_append_sheet(wb, ws1, 'Problema');

    // Hoja 2: Solución
    const solucionData = [];
    solucionData.push(['SOLUCIÓN ÓPTIMA']);
    solucionData.push([]);
    solucionData.push(['Variable', 'Valor']);

    const solucionElement = document.querySelector('.alert-success');
    if (solucionElement) {
        const variables = solucionElement.querySelectorAll('.col-md-6 strong');
        variables.forEach(variable => {
            const texto = variable.textContent;
            const partes = texto.split(' = ');
            if (partes.length === 2) {
                solucionData.push([partes[0], parseFloat(partes[1])]);
            }
        });

        solucionData.push([]);
        const valorOptimo = document.querySelector('#valor-optimo');
        if (valorOptimo) {
            const valorTexto = valorOptimo.textContent.replace(/[^\w\s=.:,-]/g, '');
            const valorMatch = valorTexto.match(/Z = ([\d.]+)/);
            if (valorMatch) {
                solucionData.push(['VALOR ÓPTIMO', parseFloat(valorMatch[1])]);
            }
        }
    }

    // Método utilizado
    solucionData.push([]);
    const metodoElement = document.querySelector('.metodo-indicator');
    if (metodoElement) {
        solucionData.push(['Método Utilizado:', metodoElement.textContent.trim()]);
    }

    const ws2 = XLSX.utils.aoa_to_sheet(solucionData);
    XLSX.utils.book_append_sheet(wb, ws2, 'Solución');

    // Hoja por cada iteración: Tablas y cálculos
    const pasosContainer = document.querySelector('.solution-steps');
    if (pasosContainer) {
        let iteracion = 1;
        let iteracionData = [];
        let hayTabla = false;
        let hayCalculos = false;
        let nombreIteracion = '';
        pasosContainer.childNodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                // Si es un título de iteración, guardar la hoja anterior y empezar nueva
                if (["H3", "H4", "H5"].includes(node.tagName) && node.textContent.match(/Iteración|Tabla|Paso/i)) {
                    // Guardar solo si hay datos reales (más que el título)
                    if (iteracionData.length > 1) {
                        let nombreHoja = nombreIteracion || `Iteración ${iteracion}`;
                        // Asegurar nombre único
                        let base = nombreHoja;
                        let sufijo = 1;
                        while (hojaNombres.has(nombreHoja)) {
                            nombreHoja = `${base}_${sufijo}`;
                            sufijo++;
                        }
                        hojaNombres.add(nombreHoja);
                        const wsIter = XLSX.utils.aoa_to_sheet(iteracionData);
                        XLSX.utils.book_append_sheet(wb, wsIter, nombreHoja);
                        iteracion++;
                    }
                    iteracionData = [[node.textContent]];
                    nombreIteracion = node.textContent.replace(/[^\w\d ]/g, '').substring(0, 30).trim();
                    hayTabla = false;
                    hayCalculos = false;
                } else if (node.tagName === 'DIV' && node.classList.contains('simplex-table-container')) {
                    // Extraer tabla de iteración
                    const tabla = node.querySelector('table');
                    if (tabla) {
                        if (!hayTabla) {
                            iteracionData.push([]);
                            iteracionData.push(['TABLA SIMPLEX']);
                            // Encabezados claros si existen
                            const encabezados = tabla.querySelectorAll('thead th');
                            if (encabezados.length > 0) {
                                const filaEncabezado = [];
                                encabezados.forEach(th => filaEncabezado.push(th.textContent.trim()));
                                iteracionData.push(filaEncabezado);
                            }
                            hayTabla = true;
                        }
                        const filas = tabla.querySelectorAll('tbody tr');
                        filas.forEach(fila => {
                            const celdas = fila.querySelectorAll('th, td');
                            const filaData = [];
                            celdas.forEach(celda => {
                                filaData.push(celda.textContent.trim());
                            });
                            if (filaData.length > 0) {
                                iteracionData.push(filaData);
                            }
                        });
                        iteracionData.push([]);
                    }
                } else if (node.tagName === 'TABLE') {
                    // Extraer tabla de iteración si está suelta
                    if (!hayTabla) {
                        iteracionData.push([]);
                        iteracionData.push(['TABLA SIMPLEX']);
                        // Encabezados claros si existen
                        const encabezados = node.querySelectorAll('thead th');
                        if (encabezados.length > 0) {
                            const filaEncabezado = [];
                            encabezados.forEach(th => filaEncabezado.push(th.textContent.trim()));
                            iteracionData.push(filaEncabezado);
                        }
                        hayTabla = true;
                    }
                    const filas = node.querySelectorAll('tbody tr');
                    filas.forEach(fila => {
                        const celdas = fila.querySelectorAll('th, td');
                        const filaData = [];
                        celdas.forEach(celda => {
                            filaData.push(celda.textContent.trim());
                        });
                        if (filaData.length > 0) {
                            iteracionData.push(filaData);
                        }
                    });
                    iteracionData.push([]);
                } else if (node.tagName === 'DIV') {
                    // Cálculos o explicaciones
                    if (node.textContent.trim().length > 0) {
                        if (!hayCalculos) {
                            iteracionData.push([]);
                            iteracionData.push(['CÁLCULOS SIMPLEX']);
                            hayCalculos = true;
                        }
                        iteracionData.push([node.textContent.trim()]);
                    }
                } else if (node.tagName === 'P') {
                    // Cálculos o explicaciones
                    if (node.textContent.trim().length > 0) {
                        if (!hayCalculos) {
                            iteracionData.push([]);
                            iteracionData.push(['CÁLCULOS SIMPLEX']);
                            hayCalculos = true;
                        }
                        iteracionData.push([node.textContent.trim()]);
                    }
                }
            }
        });
        // Guardar la última iteración si hay datos reales
        if (iteracionData.length > 1) {
            let nombreHoja = nombreIteracion || `Iteración ${iteracion}`;
            let base = nombreHoja;
            let sufijo = 1;
            while (hojaNombres.has(nombreHoja)) {
                nombreHoja = `${base}_${sufijo}`;
                sufijo++;
            }
            hojaNombres.add(nombreHoja);
            const wsIter = XLSX.utils.aoa_to_sheet(iteracionData);
            XLSX.utils.book_append_sheet(wb, wsIter, nombreHoja);
        }
    }

    // Guardar archivo
    XLSX.writeFile(wb, 'simplex-solucion.xlsx');

    // Mostrar mensaje de éxito
    Swal.fire({
        icon: 'success',
        title: '¡Exportado!',
        text: 'El archivo Excel se ha descargado correctamente.',
        timer: 2000,
        showConfirmButton: false
    });
}

// Funciones auxiliares
function obtenerFuncionObjetivo() {
    const coeficientes = [];
    const variables = [];
    
    // Obtener coeficientes de la función objetivo
    const objetivoInputs = document.querySelectorAll('#objetivo-coeficientes input');
    objetivoInputs.forEach((input, index) => {
        const valor = parseFloat(input.value) || 0;
        if (valor !== 0) {
            const variableInput = document.querySelector(`input[name="variable_${index}"]`);
            const nombreVariable = variableInput ? variableInput.value : `x${index + 1}`;
            
            if (coeficientes.length > 0) {
                if (valor > 0) {
                    coeficientes.push(` + ${valor}${nombreVariable}`);
                } else {
                    coeficientes.push(` ${valor}${nombreVariable}`);
                }
            } else {
                coeficientes.push(`${valor}${nombreVariable}`);
            }
        }
    });
    
    return coeficientes.join('');
}

function obtenerRestricciones() {
    const restricciones = [];
    const filas = document.querySelectorAll('#restricciones-tbody tr');
    
    filas.forEach(fila => {
        const coefInputs = fila.querySelectorAll('input[type="number"]:not([name*="valor"])');
        const tipoSelect = fila.querySelector('select');
        const valorInput = fila.querySelector('input[name*="valor"]');
        
        if (coefInputs.length > 0 && tipoSelect && valorInput) {
            const coeficientes = [];
            
            coefInputs.forEach((input, index) => {
                const valor = parseFloat(input.value) || 0;
                if (valor !== 0) {
                    const variableInput = document.querySelector(`input[name="variable_${index}"]`);
                    const nombreVariable = variableInput ? variableInput.value : `x${index + 1}`;
                    
                    if (coeficientes.length > 0) {
                        if (valor > 0) {
                            coeficientes.push(` + ${valor}${nombreVariable}`);
                        } else {
                            coeficientes.push(` ${valor}${nombreVariable}`);
                        }
                    } else {
                        coeficientes.push(`${valor}${nombreVariable}`);
                    }
                }
            });
            
            if (coeficientes.length > 0) {
                const restriccion = `${coeficientes.join('')} ${tipoSelect.value} ${valorInput.value}`;
                restricciones.push(restriccion);
            }
        }
    });
    
    return restricciones;
}