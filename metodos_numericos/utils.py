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
    
    # Fila de la función objetivo (negativa para maximización)
    fila_obj = [-coef for coef in c] + [0]
    tabla.append(fila_obj)
    
    iteracion = 0
    tablas_simplex = []
    
    while True:
        iteracion += 1
        pasos.append(f"ITERACIÓN {iteracion}")
        pasos.append("")
        
        # Mostrar tabla actual
        tabla_info = _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos)
        tablas_simplex.append(tabla_info)
        
        # Verificar optimalidad
        fila_obj_actual = tabla[-1][:-1]
        if all(coef >= 0 for coef in fila_obj_actual):
            pasos.append("✓ Todos los coeficientes en la fila objetivo son ≥ 0")
            pasos.append("¡SOLUCIÓN ÓPTIMA ENCONTRADA!")
            break
        
        # Encontrar variable entrante (columna pivote)
        col_pivote = min(range(len(fila_obj_actual)), key=lambda i: fila_obj_actual[i])
        pasos.append(f"Variable entrante: columna {col_pivote + 1} (coeficiente más negativo: {fila_obj_actual[col_pivote]})")
        
        # Encontrar variable saliente (fila pivote) usando prueba de razón mínima
        razones = []
        for i in range(m):
            if tabla[i][col_pivote] > 0:
                razon = tabla[i][-1] / tabla[i][col_pivote]
                razones.append((razon, i))
            else:
                razones.append((float('inf'), i))
        
        if all(r[0] == float('inf') for r in razones):
            pasos.append("❌ Solución no acotada (todos los coeficientes ≤ 0)")
            return {
                'error': 'Solución no acotada',
                'pasos': pasos,
                'tablas': tablas_simplex
            }
        
        razon_min, fila_pivote = min(razones)
        pasos.append(f"Variable saliente: {variables_basicas[fila_pivote]} (razón mínima: {razon_min})")
        
        # Elemento pivote
        pivote = tabla[fila_pivote][col_pivote]
        pasos.append(f"Elemento pivote: {pivote}")
        pasos.append("")
        
        # Operaciones de pivoteo
        pasos.append("Operaciones de pivoteo:")
        
        # Normalizar fila pivote
        pasos.append(f"1. Dividir fila {fila_pivote + 1} por {pivote}:")
        for j in range(len(tabla[fila_pivote])):
            tabla[fila_pivote][j] /= pivote
        
        # Eliminar en otras filas
        for i in range(len(tabla)):
            if i != fila_pivote and tabla[i][col_pivote] != 0:
                factor = tabla[i][col_pivote]
                pasos.append(f"2. F{i+1} = F{i+1} - ({factor}) * F{fila_pivote+1}")
                for j in range(len(tabla[i])):
                    tabla[i][j] -= factor * tabla[fila_pivote][j]
        
        # Actualizar variable básica
        if col_pivote < num_vars_originales:
            variables_basicas[fila_pivote] = f"x{col_pivote + 1}"
        else:
            variables_basicas[fila_pivote] = f"s{col_pivote - num_vars_originales + 1}"
        
        pasos.append("")
        
        if iteracion > 20:  # Prevenir bucles infinitos
            pasos.append("❌ Demasiadas iteraciones - posible ciclo")
            break
    
    # Extraer solución
    solucion = [0] * num_vars_originales
    for i, var in enumerate(variables_basicas):
        if var.startswith('x'):
            var_num = int(var[1:]) - 1
            if var_num < num_vars_originales:
                solucion[var_num] = tabla[i][-1]
    
    valor_objetivo = tabla[-1][-1]
    if tipo_original == 'minimizar':
        valor_objetivo = -valor_objetivo
    
    pasos.append("")
    pasos.append("3. SOLUCIÓN ÓPTIMA")
    pasos.append("")
    for i, val in enumerate(solucion):
        pasos.append(f"x{i+1} = {val:.6f}")
    pasos.append(f"Valor óptimo de Z = {valor_objetivo:.6f}")
    
    return {
        'solucion': solucion,
        'valor_objetivo': valor_objetivo,
        'pasos': pasos,
        'tablas': tablas_simplex,
        'variables_basicas': variables_basicas,
        'tipo_optimizacion': tipo_original
    }

def _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos):
    """Muestra la tabla Simplex de manera formateada"""
    
    m = len(tabla) - 1  # número de restricciones
    n = len(tabla[0]) - 1  # número de variables
    
    pasos.append("Tabla Simplex:")
    pasos.append("")
    
    # Encabezado
    encabezado = "Base".ljust(8)
    for j in range(n):
        if j < len(variables_basicas):
            encabezado += f"x{j+1}".rjust(10)
        else:
            encabezado += f"s{j-len(variables_basicas)+1}".rjust(10)
    encabezado += "RHS".rjust(12)
    pasos.append(encabezado)
    pasos.append("-" * len(encabezado))
    
    # Filas de restricciones
    for i in range(m):
        fila = variables_basicas[i].ljust(8)
        for j in range(len(tabla[i])):
            fila += f"{tabla[i][j]:10.4f}"
        pasos.append(fila)
    
    # Fila objetivo
    fila_z = "Z".ljust(8)
    for j in range(len(tabla[-1])):
        fila_z += f"{tabla[-1][j]:10.4f}"
    pasos.append(fila_z)
    pasos.append("")
    
    return {
        'iteracion': iteracion,
        'tabla': [fila[:] for fila in tabla],  # Copia profunda
        'variables_basicas': variables_basicas[:]
    }