// Función para dividir por espacios (filtro personalizado)
function splitBySpaces(str) {
    return str.trim().split(/\s+/);
}

// Función para alternar tema
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

// Actualiza el icono y las clases del botón según el tema
function updateThemeButton(theme) {
    const icon = document.getElementById('theme-icon');
    const boton = document.querySelector('.theme-toggle');
    const body = document.body;
    if (theme === 'dark') {
        if (icon) icon.className = 'fas fa-sun';
        if (boton) {
            boton.classList.remove('bg-secondary-neon');
            boton.classList.add('bg-warning-neon');
        }
        body.classList.add('bg-secondary-neon');
    } else {
        if (icon) icon.className = 'fas fa-moon';
        if (boton) {
            boton.classList.remove('bg-warning-neon');
            boton.classList.add('bg-secondary-neon');
        }
        body.classList.remove('bg-secondary-neon');
    }
}

// Cargar tema guardado
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
    enhanceSimplexTables();
    
    agregarRestriccion();
    agregarRestriccion();
    
});

function enhanceSimplexTables() {
    // Buscar todas las tablas Simplex y mejorar su visualización
    const tables = document.querySelectorAll('.simplex-table');
    
    tables.forEach(function(table, tableIndex) {
        const rows = table.querySelectorAll('tbody tr');
        
        // Detectar información de pivote desde los pasos
        const pasos = document.querySelectorAll('.solution-steps p, .solution-steps .alert');
        let filaPivote = -1;
        let columnaPivote = -1;
        
        // Buscar información de pivote en los pasos
        pasos.forEach(function(paso) {
            const texto = paso.textContent || paso.innerText;
            
            // Buscar variable entrante (columna pivote)
            const matchEntrante = texto.match(/VARIABLE ENTRANTE:.*columna (\d+)/);
            if (matchEntrante) {
                columnaPivote = parseInt(matchEntrante[1]) - 1; // Convertir a índice base 0
            }
            
            // Buscar variable saliente (fila pivote)
            const matchSaliente = texto.match(/VARIABLE SALIENTE:.*fila (\d+)/);
            if (matchSaliente) {
                filaPivote = parseInt(matchSaliente[1]) - 1; // Convertir a índice base 0
            }
        });
        
        // Aplicar estilos de pivote si se encontraron
        if (filaPivote >= 0 && columnaPivote >= 0) {
            highlightPivotElements(table, filaPivote, columnaPivote);
        }
        
        // Marcar la última fila como fila objetivo
        rows.forEach(function(row, rowIndex) {
            const cells = row.querySelectorAll('td');
            
            if (cells.length > 0 && cells[0].textContent.trim() === 'Z') {
                row.classList.add('objective-row');
            }
        });
        
        // Agregar hover effects mejorados
        addHoverEffects(table);
    });
}

function highlightPivotElements(table, pivotRow, pivotCol) {
    const rows = table.querySelectorAll('tbody tr');
    
    // Resaltar columna entrante (excluyendo fila objetivo)
    rows.forEach(function(row, rowIndex) {
        const cells = row.querySelectorAll('td');
        if (cells[pivotCol + 1] && !row.classList.contains('objective-row')) { // +1 porque la primera columna es la base
            cells[pivotCol + 1].classList.add('entering-variable');
        }
    });
    
    // Resaltar fila saliente
    if (rows[pivotRow]) {
        const cells = rows[pivotRow].querySelectorAll('td');
        cells.forEach(function(cell, cellIndex) {
            if (cellIndex > 0) { // Excluir columna base
                cell.classList.add('leaving-variable');
            }
        });
        rows[pivotRow].classList.add('pivot-row');
    }
    
    // Resaltar elemento pivote
    if (rows[pivotRow] && rows[pivotRow].querySelectorAll('td')[pivotCol + 1]) {
        const pivotCell = rows[pivotRow].querySelectorAll('td')[pivotCol + 1];
        pivotCell.classList.add('pivot-cell');
        
        // Agregar tooltip con información del pivote
        pivotCell.title = `Elemento Pivote: ${pivotCell.textContent.trim()}`;
    }
    
    // Resaltar encabezados de columna y fila pivote
    const headers = table.querySelectorAll('thead th');
    if (headers[pivotCol + 1]) {
        headers[pivotCol + 1].style.backgroundColor = '#007bff';
        headers[pivotCol + 1].style.color = 'white';
    }
}

function addHoverEffects(table) {
    const cells = table.querySelectorAll('td');
    
    cells.forEach(function(cell) {
        cell.addEventListener('mouseenter', function() {
            // Resaltar fila y columna al hacer hover
            const row = this.parentElement;
            const cellIndex = Array.from(row.children).indexOf(this);
            
            // Resaltar fila
            Array.from(row.children).forEach(function(c) {
                c.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
            });
            
            // Resaltar columna
            const table = row.closest('table');
            const rows = table.querySelectorAll('tr');
            rows.forEach(function(r) {
                if (r.children[cellIndex]) {
                    // Usar un color más oscuro en modo claro
                    if (document.documentElement.getAttribute('data-theme') === 'dark') {
                        r.children[cellIndex].style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
                    } else {
                        r.children[cellIndex].style.backgroundColor = 'rgba(0, 60, 130, 0.18)';
                        
                    }
                }
            });
        });
        
        cell.addEventListener('mouseleave', function() {
            // Restaurar colores originales
            const row = this.parentElement;
            const cellIndex = Array.from(row.children).indexOf(this);
            
            // Restaurar fila
            Array.from(row.children).forEach(function(c) {
                c.style.backgroundColor = '';
            });
            
            // Restaurar columna
            const table = row.closest('table');
            const rows = table.querySelectorAll('tr');
            rows.forEach(function(r) {
                if (r.children[cellIndex]) {
                    r.children[cellIndex].style.backgroundColor = '';
                }
            });
        });
    });
}

let contadorRestricciones = 0;

function agregarRestriccion() {
    const container = document.getElementById('restricciones-container');
    const div = document.createElement('div');
    div.className = 'mb-2 p-2 border rounded';
    div.innerHTML = `
        <div class="row">
            <div class="col-5 col-lg-4 col-xl-5 m-0">
                <input type="text" class="form-control form-control-sm" 
                       name="restriccion_${contadorRestricciones}_coeficientes" 
                       placeholder="1,2,1" required>
                <small class="text-muted">Coeficientes</small>
            </div>
            <div class="col-2 col-lg-4 col-xl-3 m-0">
                <select class="form-select form-select-sm" 
                        name="restriccion_${contadorRestricciones}_tipo">
                    <option value="<=">&le;</option>
                    <option value=">=">&ge;</option>
                    <option value="=">=</option>
                </select>
            </div>
            <div class="col-3 col-lg-4 col-xl-4 m-0">
                <input type="number" class="form-control form-control-sm" 
                       name="restriccion_${contadorRestricciones}_valor" 
                       placeholder="0" step="any" required>
                <small class="text-muted">Valor</small>
            </div>
            <div class="col-2 col-lg-12">
                <button type="button" class="btn btn-outline-danger btn-sm ancho" 
                        onclick="this.parentElement.parentElement.parentElement.remove()">
                    <i class="fas fa-trash"></i> 
                    <span class="d-none d-md-inline">Eliminar</span>
                </button>
            </div>
        </div>
    `;
    container.appendChild(div);
    contadorRestricciones++;
}

function cargarRestricciones(restricciones) {
    const container = document.getElementById('restricciones-container');
    container.innerHTML = ''; // Limpiar contenedor
    
    restricciones.forEach(function(rest, index) {
        const div = document.createElement('div');
        div.className = 'mb-2 p-2 border rounded';
        div.innerHTML = `
            <div class="row">
                <div class="col-5 col-lg-4 col-xl-5 m-0">
                    <input type="text" class="form-control form-control-sm" 
                           name="restriccion_${index}_coeficientes" 
                           placeholder="1,2,1" value="${rest.coeficientes}" required>
                    <small class="text-muted">Coeficientes</small>
                </div>
                <div class="col-2 col-lg-4 col-xl-3 m-0">
                    <select class="form-select form-select-sm" 
                            name="restriccion_${index}_tipo">
                        <option value="<=" ${rest.tipo === '<=' ? 'selected' : ''}>&le;</option>
                        <option value=">=" ${rest.tipo === '>=' ? 'selected' : ''}>&ge;</option>
                        <option value="=" ${rest.tipo === '=' ? 'selected' : ''}>=</option>
                    </select>
                </div>
                <div class="col-3 col-lg-4 col-xl-4 m-0">
                    <input type="number" class="form-control form-control-sm" 
                           name="restriccion_${index}_valor" 
                           placeholder="0" step="any" value="${rest.valor}" required>
                    <small class="text-muted">Valor</small>
                </div>
                <div class="col-2 col-lg-12">
                    <button type="button" class="btn btn-outline-danger btn-sm ancho" 
                            onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-trash"></i> 
                        <span class="d-none d-md-inline">Eliminar</span>
                    </button>
                </div>
            </div>
        `;
        container.appendChild(div);
    });
    
    contadorRestricciones = restricciones.length;
}

// Validación en tiempo real
document.addEventListener('input', function(e) {
    if (e.target.name && e.target.name.includes('coeficientes')) {
        validateCoefficients(e.target);
    } else if (e.target.name && e.target.name.includes('valor')) {
        validateValue(e.target);
    }
});

function validateCoefficients(input) {
    const value = input.value.trim();
    const isValid = /^-?\d*\.?\d*(\s*,\s*-?\d*\.?\d*)*$/.test(value);
    
    if (value && !isValid) {
        input.classList.add('is-invalid');
        showTooltip(input, 'Formato: números separados por comas (ej: 1,2,-3)');
    } else {
        input.classList.remove('is-invalid');
        hideTooltip(input);
    }
}

function validateValue(input) {
    const value = input.value.trim();
    const isValid = /^-?\d*\.?\d*$/.test(value);
    
    if (value && !isValid) {
        input.classList.add('is-invalid');
        showTooltip(input, 'Debe ser un número válido');
    } else {
        input.classList.remove('is-invalid');
        hideTooltip(input);
    }
}

function showTooltip(element, message) {
    // Implementación simple de tooltip
    element.title = message;
}

function hideTooltip(element) {
    element.title = '';
}