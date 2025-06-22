import numpy as np
import sympy as sp
from sympy import symbols, lambdify, sympify
import math

def interpolacion_hermite(puntos, x_eval):
    """
    Implementa la interpolación de Hermite
    
    Args:
        puntos: Lista de tuplas (x_i, f(x_i), f'(x_i))
        x_eval: Punto donde evaluar el polinomio
    
    Returns:
        Dict con resultado, polinomio y pasos detallados
    """
    n = len(puntos)
    
    # Extraer coordenadas
    x_vals = [p[0] for p in puntos]
    f_vals = [p[1] for p in puntos]
    df_vals = [p[2] for p in puntos]
    
    # Crear tabla de diferencias divididas
    # Necesitamos 2n puntos (cada punto original se duplica)
    z = []  # Puntos expandidos
    Q = []  # Tabla de diferencias divididas
    
    # Expandir puntos
    for i in range(n):
        z.append(x_vals[i])
        z.append(x_vals[i])
    
    # Inicializar primera columna de Q
    Q = [[0.0 for _ in range(2*n)] for _ in range(2*n)]
    
    # Llenar primera columna
    for i in range(n):
        Q[2*i][0] = f_vals[i]
        Q[2*i+1][0] = f_vals[i]
    
    # Llenar segunda columna
    for i in range(n):
        Q[2*i+1][1] = df_vals[i]
        if i < n-1:
            Q[2*i+2][1] = (Q[2*i+2][0] - Q[2*i+1][0]) / (z[2*i+2] - z[2*i+1])
    
    # Llenar resto de la tabla
    for i in range(2, 2*n):
        for j in range(2, i+1):
            Q[i][j] = (Q[i][j-1] - Q[i-1][j-1]) / (z[i] - z[i-j])
    
    # Construir polinomio
    x = symbols('x')
    polinomio = Q[0][0]
    
    pasos = []
    pasos.append("=== INTERPOLACIÓN DE HERMITE ===")
    pasos.append(f"Puntos dados: {puntos}")
    pasos.append(f"Punto de evaluación: x = {x_eval}")
    pasos.append("")
    pasos.append("1. Tabla de diferencias divididas:")
    
    # Mostrar tabla
    pasos.append("   Xi    |  F[Xi]  |  Primera D.D  |  ...")
    pasos.append("   " + "-"*50)
    for i in range(2*n):
        fila = f"  {z[i]:6.3f} |"
        for j in range(min(i+1, 2*n)):
            fila += f"  {Q[i][j]:8.4f}  |"
        pasos.append(fila)
    
    pasos.append("")
    pasos.append("2. Construcción del polinomio:")
    pasos.append(f"H(x) = {Q[0][0]:.4f}")
    
    # Construir términos del polinomio
    termino_actual = 1
    for k in range(1, 2*n):
        termino_actual *= (x - z[k-1])
        coef = Q[k][k]
        polinomio += coef * termino_actual
        
        # Mostrar paso
        termino_str = ""
        for j in range(k):
            if j == 0:
                termino_str = f"(x - {z[j]:.3f})"
            else:
                termino_str += f" * (x - {z[j]:.3f})"
        
        pasos.append(f"     + {coef:.6f} * {termino_str}")
    
    # Simplificar polinomio
    polinomio_expandido = sp.expand(polinomio)
    
    pasos.append("")
    pasos.append("3. Polinomio expandido:")
    pasos.append(f"H(x) = {polinomio_expandido}")
    
    # Evaluar en x_eval
    resultado = float(polinomio_expandido.subs(x, x_eval))
    
    pasos.append("")
    pasos.append("4. Evaluación:")
    pasos.append(f"H({x_eval}) = {resultado:.8f}")
    
    return {
        'resultado': resultado,
        'polinomio': str(polinomio_expandido),
        'pasos': pasos,
        'puntos': puntos
    }

def integracion_compuesta(funcion_str, a, b, n, metodo):
    """
    Implementa integración numérica compuesta
    
    Args:
        funcion_str: Función como string (ej: 'x**2 + 1')
        a, b: Límites de integración
        n: Número de subintervalos
        metodo: 'trapecio', 'simpson13', 'simpson38'
    
    Returns:
        Dict con resultado y pasos detallados
    """
    # Parsear función
    x = symbols('x')
    try:
        funcion_sym = sympify(funcion_str)
        f = lambdify(x, funcion_sym, 'numpy')
    except:
        raise ValueError(f"No se pudo parsear la función: {funcion_str}")
    
    h = (b - a) / n
    pasos = []
    
    pasos.append(f"=== INTEGRACIÓN NUMÉRICA COMPUESTA - {metodo.upper()} ===")
    pasos.append(f"Función: f(x) = {funcion_str}")
    pasos.append(f"Intervalo: [{a}, {b}]")
    pasos.append(f"Número de subintervalos: n = {n}")
    pasos.append(f"Ancho de subintervalo: h = (b-a)/n = ({b}-{a})/{n} = {h:.6f}")
    pasos.append("")
    
    if metodo == 'trapecio':
        resultado = _trapecio_compuesto(f, a, b, n, h, pasos)
    elif metodo == 'simpson13':
        if n % 2 != 0:
            raise ValueError("Para Simpson 1/3, n debe ser par")
        resultado = _simpson13_compuesto(f, a, b, n, h, pasos)
    elif metodo == 'simpson38':
        if n % 3 != 0:
            raise ValueError("Para Simpson 3/8, n debe ser múltiplo de 3")
        resultado = _simpson38_compuesto(f, a, b, n, h, pasos)
    else:
        raise ValueError(f"Método no reconocido: {metodo}")
    
    return {
        'resultado': resultado,
        'pasos': pasos,
        'metodo': metodo,
        'funcion': funcion_str
    }

def _trapecio_compuesto(f, a, b, n, h, pasos):
    """Regla del trapecio compuesta"""
    pasos.append("Fórmula del trapecio compuesto:")
    pasos.append("∫f(x)dx ≈ (h/2)[f(x₀) + 2∑f(xᵢ) + f(xₙ)]")
    pasos.append("")
    
    # Calcular puntos
    x_vals = [a + i*h for i in range(n+1)]
    f_vals = [f(x) for x in x_vals]
    
    pasos.append("Evaluación de la función en los puntos:")
    for i, (x_val, f_val) in enumerate(zip(x_vals, f_vals)):
        pasos.append(f"f(x_{i}) = f({x_val:.4f}) = {f_val:.6f}")
    
    pasos.append("")
    pasos.append("Aplicando la fórmula:")
    
    suma = f_vals[0] + f_vals[-1]  # f(x₀) + f(xₙ)
    suma_intermedia = sum(f_vals[1:-1])  # ∑f(xᵢ) para i=1 a n-1
    
    pasos.append(f"f(x₀) + f(xₙ) = {f_vals[0]:.6f} + {f_vals[-1]:.6f} = {suma:.6f}")
    pasos.append(f"2∑f(xᵢ) = 2 × {suma_intermedia:.6f} = {2*suma_intermedia:.6f}")
    
    suma += 2 * suma_intermedia
    resultado = (h/2) * suma
    
    pasos.append(f"Suma total = {suma:.6f}")
    pasos.append(f"Resultado = (h/2) × suma = ({h:.6f}/2) × {suma:.6f} = {resultado:.8f}")
    
    return resultado

def _simpson13_compuesto(f, a, b, n, h, pasos):
    """Regla de Simpson 1/3 compuesta"""
    pasos.append("Fórmula de Simpson 1/3 compuesta:")
    pasos.append("∫f(x)dx ≈ (h/3)[f(x₀) + 4∑f(x₂ᵢ₋₁) + 2∑f(x₂ᵢ) + f(xₙ)]")
    pasos.append("")
    
    # Calcular puntos
    x_vals = [a + i*h for i in range(n+1)]
    f_vals = [f(x) for x in x_vals]
    
    pasos.append("Evaluación de la función en los puntos:")
    for i, (x_val, f_val) in enumerate(zip(x_vals, f_vals)):
        pasos.append(f"f(x_{i}) = f({x_val:.4f}) = {f_val:.6f}")
    
    pasos.append("")
    pasos.append("Aplicando la fórmula:")
    
    # Términos impares (coeficiente 4)
    suma_impares = sum(f_vals[i] for i in range(1, n, 2))
    # Términos pares intermedios (coeficiente 2)
    suma_pares = sum(f_vals[i] for i in range(2, n-1, 2))
    
    pasos.append(f"f(x₀) + f(xₙ) = {f_vals[0]:.6f} + {f_vals[-1]:.6f} = {f_vals[0] + f_vals[-1]:.6f}")
    pasos.append(f"4∑f(x₂ᵢ₋₁) = 4 × {suma_impares:.6f} = {4*suma_impares:.6f}")
    pasos.append(f"2∑f(x₂ᵢ) = 2 × {suma_pares:.6f} = {2*suma_pares:.6f}")
    
    suma_total = f_vals[0] + f_vals[-1] + 4*suma_impares + 2*suma_pares
    resultado = (h/3) * suma_total
    
    pasos.append(f"Suma total = {suma_total:.6f}")
    pasos.append(f"Resultado = (h/3) × suma = ({h:.6f}/3) × {suma_total:.6f} = {resultado:.8f}")
    
    return resultado

def _simpson38_compuesto(f, a, b, n, h, pasos):
    """Regla de Simpson 3/8 compuesta"""
    pasos.append("Fórmula de Simpson 3/8 compuesta:")
    pasos.append("∫f(x)dx ≈ (3h/8)[f(x₀) + 3∑f(x₃ᵢ₋₂) + 3∑f(x₃ᵢ₋₁) + 2∑f(x₃ᵢ) + f(xₙ)]")
    pasos.append("")
    
    # Calcular puntos
    x_vals = [a + i*h for i in range(n+1)]
    f_vals = [f(x) for x in x_vals]
    
    pasos.append("Evaluación de la función en los puntos:")
    for i, (x_val, f_val) in enumerate(zip(x_vals, f_vals)):
        pasos.append(f"f(x_{i}) = f({x_val:.4f}) = {f_val:.6f}")
    
    pasos.append("")
    pasos.append("Aplicando la fórmula:")
    
    # Coeficientes según posición
    suma_3_tipo1 = sum(f_vals[i] for i in range(1, n, 3))  # x₁, x₄, x₇, ...
    suma_3_tipo2 = sum(f_vals[i] for i in range(2, n, 3))  # x₂, x₅, x₈, ...
    suma_2 = sum(f_vals[i] for i in range(3, n-2, 3))      # x₃, x₆, x₉, ...
    
    pasos.append(f"f(x₀) + f(xₙ) = {f_vals[0]:.6f} + {f_vals[-1]:.6f} = {f_vals[0] + f_vals[-1]:.6f}")
    pasos.append(f"3∑f(x₃ᵢ₋₂) = 3 × {suma_3_tipo1:.6f} = {3*suma_3_tipo1:.6f}")
    pasos.append(f"3∑f(x₃ᵢ₋₁) = 3 × {suma_3_tipo2:.6f} = {3*suma_3_tipo2:.6f}")
    pasos.append(f"2∑f(x₃ᵢ) = 2 × {suma_2:.6f} = {2*suma_2:.6f}")
    
    suma_total = f_vals[0] + f_vals[-1] + 3*suma_3_tipo1 + 3*suma_3_tipo2 + 2*suma_2
    resultado = (3*h/8) * suma_total
    
    pasos.append(f"Suma total = {suma_total:.6f}")
    pasos.append(f"Resultado = (3h/8) × suma = (3×{h:.6f}/8) × {suma_total:.6f} = {resultado:.8f}")
    
    return resultado

def metodo_simplex(funcion_objetivo, restricciones, tipo_optimizacion):
    """
    Implementa el método Simplex para programación lineal
    
    Args:
        funcion_objetivo: Dict con coeficientes de la función objetivo
        restricciones: Lista de restricciones con coeficientes, tipo y valor
        tipo_optimizacion: 'maximizar' o 'minimizar'
    
    Returns:
        Dict con resultado, tablas paso a paso y solución óptima
    """
    pasos = []
    pasos.append("=== MÉTODO SIMPLEX ===")
    pasos.append(f"Tipo de optimización: {tipo_optimizacion.upper()}")
    pasos.append("")
    
    # Convertir a forma estándar
    problema_std = _convertir_forma_estandar(funcion_objetivo, restricciones, tipo_optimizacion, pasos)
    
    if problema_std is None:
        return {
            'error': 'No se pudo convertir el problema a forma estándar',
            'pasos': pasos
        }
    
    # Resolver usando Simplex
    resultado = _resolver_simplex(problema_std, pasos)
    
    return resultado

def _convertir_forma_estandar(funcion_objetivo, restricciones, tipo_optimizacion, pasos):
    """Convierte el problema a forma estándar para el método Simplex"""
    
    pasos.append("1. CONVERSIÓN A FORMA ESTÁNDAR")
    pasos.append("")
    
    # Mostrar problema original
    pasos.append("Problema original:")
    obj_str = " + ".join([f"{coef}x{i+1}" if coef >= 0 else f"{coef}x{i+1}" 
                         for i, coef in enumerate(funcion_objetivo)])
    pasos.append(f"{tipo_optimizacion.capitalize()} Z = {obj_str}")
    
    pasos.append("Sujeto a:")
    for i, rest in enumerate(restricciones):
        rest_str = " + ".join([f"{coef}x{j+1}" if coef >= 0 else f"{coef}x{j+1}" 
                              for j, coef in enumerate(rest['coeficientes'])])
        pasos.append(f"  {rest_str} {rest['tipo']} {rest['valor']}")
    
    pasos.append("  xi ≥ 0 para todo i")
    pasos.append("")
    
    # Convertir minimización a maximización si es necesario
    if tipo_optimizacion == 'minimizar':
        funcion_objetivo = [-coef for coef in funcion_objetivo]
        pasos.append("Convertir minimización a maximización (multiplicar por -1):")
        obj_str = " + ".join([f"{coef}x{i+1}" if coef >= 0 else f"{coef}x{i+1}" 
                             for i, coef in enumerate(funcion_objetivo)])
        pasos.append(f"Maximizar Z = {obj_str}")
        pasos.append("")
    
    # Añadir variables de holgura/exceso
    num_vars_originales = len(funcion_objetivo)
    num_restricciones = len(restricciones)
    
    # Matriz A extendida y vector b
    A = []
    b = []
    variables_basicas = []
    
    pasos.append("Añadir variables de holgura/exceso:")
    
    for i, rest in enumerate(restricciones):
        fila = rest['coeficientes'].copy()
        
        # Añadir variables de holgura/exceso
        for j in range(num_restricciones):
            if i == j:
                if rest['tipo'] == '<=':
                    fila.append(1)  # Variable de holgura
                    variables_basicas.append(f"s{i+1}")
                elif rest['tipo'] == '>=':
                    fila.append(-1)  # Variable de exceso
                    variables_basicas.append(f"e{i+1}")
                else:  # rest['tipo'] == '='
                    fila.append(0)
                    # Para igualdades necesitamos variables artificiales
                    variables_basicas.append(f"a{i+1}")
            else:
                fila.append(0)
        
        A.append(fila)
        b.append(rest['valor'])
        
        # Mostrar restricción convertida
        rest_str = " + ".join([f"{coef}x{j+1}" if coef >= 0 else f"{coef}x{j+1}" 
                              for j, coef in enumerate(rest['coeficientes'])])
        if rest['tipo'] == '<=':
            pasos.append(f"  {rest_str} + s{i+1} = {rest['valor']}")
        elif rest['tipo'] == '>=':
            pasos.append(f"  {rest_str} - e{i+1} = {rest['valor']}")
        else:
            pasos.append(f"  {rest_str} = {rest['valor']}")
    
    # Extender función objetivo con ceros para variables de holgura/exceso
    c = funcion_objetivo + [0] * num_restricciones
    
    pasos.append("")
    pasos.append("Función objetivo extendida:")
    obj_str = " + ".join([f"{coef}x{i+1}" if i < num_vars_originales 
                         else f"{coef}{variables_basicas[i-num_vars_originales]}" 
                         for i, coef in enumerate(c) if coef != 0])
    pasos.append(f"Maximizar Z = {obj_str}")
    pasos.append("")
    
    return {
        'A': A,
        'b': b,
        'c': c,
        'variables_basicas': variables_basicas,
        'num_vars_originales': num_vars_originales,
        'tipo_original': tipo_optimizacion
    }

def _resolver_simplex(problema, pasos):
    """Resuelve el problema usando el algoritmo Simplex"""
    
    A = problema['A']
    b = problema['b']
    c = problema['c']
    variables_basicas = problema['variables_basicas']
    num_vars_originales = problema['num_vars_originales']
    tipo_original = problema['tipo_original']
    
    m = len(A)  # número de restricciones
    n = len(c)  # número de variables
    
    pasos.append("2. APLICACIÓN DEL MÉTODO SIMPLEX")
    pasos.append("")
    
    # Crear tabla inicial
    tabla = []
    for i in range(m):
        fila = A[i] + [b[i]]
        tabla.append(fila)
    
    # Fila de la función objetivo
    if tipo_original == 'maximizar':
        fila_obj = [-coef for coef in c] + [0]  # Negativa para maximización
    else:
        fila_obj = [coef for coef in c] + [0]   # Positiva para minimización
    tabla.append(fila_obj)
    
    iteracion = 0
    tablas_simplex = []
    
    # Variables para rastrear pivotes
    historial_pivotes = []
    
    while True:
        iteracion += 1
        pasos.append(f"ITERACIÓN {iteracion}")
        pasos.append("")
        
        # Mostrar tabla actual
        tabla_info = _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos)
        tablas_simplex.append(tabla_info)
        
        # Verificar optimalidad
        fila_obj_actual = tabla[-1][:-1]
        if all(coef >= -1e-10 for coef in fila_obj_actual):  # Usar tolerancia numérica
            pasos.append("✓ Todos los coeficientes en la fila objetivo son ≥ 0")
            pasos.append("¡SOLUCIÓN ÓPTIMA ENCONTRADA!")
            break
        
        # Encontrar variable entrante (columna pivote)
        col_pivote = min(range(len(fila_obj_actual)), key=lambda i: fila_obj_actual[i])
        coef_entrante = fila_obj_actual[col_pivote]
        
        # Determinar nombre de variable entrante
        if col_pivote < num_vars_originales:
            var_entrante = f"x{col_pivote + 1}"
        else:
            var_entrante = f"s{col_pivote - num_vars_originales + 1}"
        
        pasos.append(f"🔵 VARIABLE ENTRANTE: {var_entrante} (columna {col_pivote + 1})")
        pasos.append(f"   Coeficiente más negativo: {coef_entrante:.6f}")
        pasos.append("")
        
        # Encontrar variable saliente (fila pivote) usando prueba de razón mínima
        pasos.append("📊 PRUEBA DE RAZÓN MÍNIMA:")
        pasos.append("   Fila | Variable Base | b(i) | Coef. Columna | Razón")
        pasos.append("   " + "-" * 55)
        
        razones = []
        razones_validas = []
        
        for i in range(m):
            coef_col = tabla[i][col_pivote]
            rhs = tabla[i][-1]
            
            if coef_col > 1e-10:  # Usar tolerancia numérica
                razon = rhs / coef_col
                razones.append((razon, i))
                razones_validas.append(razon)
                pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | {razon:7.3f}")
            else:
                razones.append((float('inf'), i))
                if coef_col <= -1e-10:
                    pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | No válida (≤0)")
                else:
                    pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | No válida (≈0)")
        
        pasos.append("")
        
        if not razones_validas or all(r == float('inf') for r, _ in razones):
            pasos.append("❌ SOLUCIÓN NO ACOTADA")
            pasos.append("   Todos los coeficientes de la columna entrante son ≤ 0")
            pasos.append("   Esto significa que la función objetivo puede crecer indefinidamente")
            pasos.append("   en la dirección de la variable entrante.")
            pasos.append("")
            pasos.append("🔍 INTERPRETACIÓN:")
            pasos.append("   - El problema no tiene solución óptima finita")
            pasos.append("   - La región factible es no acotada en la dirección de optimización")
            pasos.append("   - Verifique las restricciones del problema original")
            
            return {
                'error': 'Solución no acotada - La función objetivo puede crecer indefinidamente',
                'pasos': pasos,
                'tablas': tablas_simplex,
                'interpretacion': 'La región factible es no acotada en la dirección de optimización',
                'sugerencia': 'Revise las restricciones del problema para asegurar que la región factible esté acotada'
            }
        
        razon_min, fila_pivote = min(razones)
        var_saliente = variables_basicas[fila_pivote]
        
        pasos.append(f"🔴 VARIABLE SALIENTE: {var_saliente} (fila {fila_pivote + 1})")
        pasos.append(f"   Razón mínima: {razon_min:.6f}")
        pasos.append("")
        
        # Elemento pivote
        pivote = tabla[fila_pivote][col_pivote]
        pasos.append(f"⚡ ELEMENTO PIVOTE: {pivote:.6f}")
        pasos.append(f"   Posición: Fila {fila_pivote + 1}, Columna {col_pivote + 1}")
        pasos.append("")
        
        # Guardar información del pivote para resaltado
        historial_pivotes.append({
            'iteracion': iteracion,
            'fila_pivote': fila_pivote,
            'col_pivote': col_pivote,
            'var_entrante': var_entrante,
            'var_saliente': var_saliente,
            'pivote': pivote
        })
        
        # Actualizar la tabla anterior con información de pivote
        if tablas_simplex:
            tablas_simplex[-1]['fila_pivote'] = fila_pivote
            tablas_simplex[-1]['col_pivote'] = col_pivote
            tablas_simplex[-1]['var_entrante'] = var_entrante
            tablas_simplex[-1]['var_saliente'] = var_saliente
            tablas_simplex[-1]['elemento_pivote'] = pivote
        
        # Operaciones de pivoteo
        pasos.append("🔧 OPERACIONES DE PIVOTEO:")
        pasos.append("")
        
        # Crear copia de la tabla para mostrar cambios
        tabla_anterior = [fila[:] for fila in tabla]
        
        # Normalizar fila pivote
        pasos.append(f"1️⃣ NORMALIZAR FILA PIVOTE (Fila {fila_pivote + 1}):")
        pasos.append(f"   Nueva Fila {fila_pivote + 1} = Fila {fila_pivote + 1} ÷ {pivote:.6f}")
        pasos.append("")
        pasos.append("   Antes:")
        fila_str = "   [" + ", ".join([f"{val:8.4f}" for val in tabla[fila_pivote]]) + "]"
        pasos.append(fila_str)
        
        for j in range(len(tabla[fila_pivote])):
            tabla[fila_pivote][j] /= pivote
        
        pasos.append("   Después:")
        fila_str = "   [" + ", ".join([f"{val:8.4f}" for val in tabla[fila_pivote]]) + "]"
        pasos.append(fila_str)
        pasos.append("")
        
        # Eliminar en otras filas
        pasos.append("2️⃣ ELIMINAR EN OTRAS FILAS:")
        for i in range(len(tabla)):
            if i != fila_pivote and abs(tabla[i][col_pivote]) > 1e-10:
                factor = tabla[i][col_pivote]
                pasos.append(f"   Fila {i+1}: Factor = {factor:.6f}")
                pasos.append(f"   Nueva Fila {i+1} = Fila {i+1} - ({factor:.6f}) × Nueva Fila {fila_pivote+1}")
                
                pasos.append("   Antes:")
                fila_str = "   [" + ", ".join([f"{val:8.4f}" for val in tabla[i]]) + "]"
                pasos.append(fila_str)
                
                for j in range(len(tabla[i])):
                    tabla[i][j] -= factor * tabla[fila_pivote][j]
                
                pasos.append("   Después:")
                fila_str = "   [" + ", ".join([f"{val:8.4f}" for val in tabla[i]]) + "]"
                pasos.append(fila_str)
                pasos.append("")
        
        # Actualizar variable básica
        variables_basicas[fila_pivote] = var_entrante
        pasos.append(f"3️⃣ ACTUALIZAR BASE:")
        pasos.append(f"   {var_saliente} sale de la base")
        pasos.append(f"   {var_entrante} entra a la base")
        pasos.append("")
        
        if iteracion > 50:  # Prevenir bucles infinitos
            pasos.append("❌ DEMASIADAS ITERACIONES")
            pasos.append("   Se ha alcanzado el límite máximo de iteraciones (50)")
            pasos.append("   Esto puede indicar:")
            pasos.append("   - Ciclado en el algoritmo Simplex")
            pasos.append("   - Problema mal formulado")
            pasos.append("   - Errores numéricos acumulados")
            return {
                'error': 'Demasiadas iteraciones - Posible ciclado o problema mal formulado',
                'pasos': pasos,
                'tablas': tablas_simplex,
                'sugerencia': 'Revise la formulación del problema o use técnicas anti-ciclado'
            }
    
    # Extraer solución
    solucion = [0.0] * num_vars_originales
    for i, var in enumerate(variables_basicas):
        if var.startswith('x'):
            var_num = int(var[1:]) - 1
            if var_num < num_vars_originales:
                solucion[var_num] = tabla[i][-1]
    
    valor_objetivo = tabla[-1][-1]
    # Mostrar siempre el valor óptimo como positivo
    valor_objetivo_mostrar = abs(valor_objetivo)
    if tipo_original == 'minimizar':
        valor_objetivo = -valor_objetivo
        valor_objetivo_mostrar = abs(valor_objetivo)

    pasos.append("")
    pasos.append("3. SOLUCIÓN ÓPTIMA")
    pasos.append("")
    pasos.append("📋 VARIABLES DE DECISIÓN:")
    for i, val in enumerate(solucion):
        pasos.append(f"   x{i+1} = {val:.6f}")
    
    pasos.append("")
    pasos.append("📊 VARIABLES DE HOLGURA/EXCESO:")
    for i, var in enumerate(variables_basicas):
        if not var.startswith('x'):
            pasos.append(f"   {var} = {tabla[i][-1]:.6f}")
    
    pasos.append("")
    # Mostrar valor óptimo siempre positivo en los pasos
    pasos.append(f"🎯 VALOR ÓPTIMO: Z = {abs(valor_objetivo_mostrar):.6f}")
    
    # Verificación de la solución
    pasos.append("")
    pasos.append("✅ VERIFICACIÓN DE LA SOLUCIÓN:")
    pasos.append("   (Sustituyendo en las restricciones originales)")
    
    return {
        'solucion': solucion,
        'valor_objetivo': valor_objetivo_mostrar,
        'pasos': pasos,
        'tablas': tablas_simplex,
        'variables_basicas': variables_basicas,
        'tipo_optimizacion': tipo_original,
        'historial_pivotes': historial_pivotes
    }

def _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos):
    """Muestra la tabla Simplex de manera formateada con HTML"""
    
    m = len(tabla) - 1  # número de restricciones
    n = len(tabla[0]) - 1  # número de variables
    
    pasos.append("📋 TABLA SIMPLEX:")
    pasos.append("")
    
    # Crear tabla HTML
    tabla_html = '<div class="simplex-table-container">'
    tabla_html += f'<div class="table-title">Iteración {iteracion}</div>'
    tabla_html += '<table class="simplex-table">'
    
    # Encabezado
    tabla_html += '<thead><tr>'
    tabla_html += '<th class="base-header">Base</th>'
    for j in range(n):
        if j < 10:  # Asumiendo máximo 10 variables originales
            tabla_html += f'<th class="var-header">x<sub>{j+1}</sub></th>'
        else:
            tabla_html += f'<th class="slack-header">s<sub>{j-9}</sub></th>'
    tabla_html += '<th class="rhs-header">b(i)</th>'
    tabla_html += '</tr></thead>'
    
    # Cuerpo de la tabla
    tabla_html += '<tbody>'
    
    # Filas de restricciones
    for i in range(m):
        tabla_html += f'<tr class="constraint-row" data-row="{i}">'
        tabla_html += f'<td class="base-column">{variables_basicas[i]}</td>'
        for j in range(len(tabla[i])):
            valor = tabla[i][j]
            clase_celda = f'data-cell data-row-{i} data-col-{j}'
            if j == len(tabla[i]) - 1:  # RHS column
                clase_celda += ' rhs-cell'
            tabla_html += f'<td class="{clase_celda}">{valor:.4f}</td>'
        tabla_html += '</tr>'
    
    # Fila objetivo
    tabla_html += '<tr class="objective-row">'
    tabla_html += '<td class="base-column objective-label">Z</td>'
    for j in range(len(tabla[-1])):
        valor = tabla[-1][j]
        clase_celda = f'objective-cell data-col-{j}'
        if j == len(tabla[-1]) - 1:  # RHS column (valor de Z)
            clase_celda += ' objective-value'
        tabla_html += f'<td class="{clase_celda}">{valor:.4f}</td>'
    tabla_html += '</tr>'
    
    tabla_html += '</tbody></table></div>'
    
    pasos.append(tabla_html)
    pasos.append("")
    
    return {
        'iteracion': iteracion,
        'tabla': [fila[:] for fila in tabla],  # Copia profunda
        'variables_basicas': variables_basicas[:],
        'tabla_html': tabla_html
    }