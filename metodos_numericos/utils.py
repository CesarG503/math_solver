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
            val = Q[i][j]
            try:
                fila += f"  {float(val):8.4f}  |"
            except Exception:
                fila += f"  {str(val):>8}  |"
        pasos.append(fila)

    pasos.append("")
    pasos.append("2. Construcción del polinomio:")
    try:
        pasos.append(f"$$H(x) = {float(Q[0][0]):.4f}$$")
        terminos_latex = [f"{float(Q[0][0]):.4f}"]
    except Exception:
        pasos.append(f"$$H(x) = {Q[0][0]}$$")
        terminos_latex = [f"{Q[0][0]}"]

    # Construir términos del polinomio
    termino_actual = 1

    for k in range(1, 2*n):
        termino_actual *= (x - z[k-1])
        coef = Q[k][k]
        polinomio += coef * termino_actual
        
        # Construir término en LaTeX
        termino_str = ""
        for j in range(k):
            if j == 0:
                termino_str = f"(x - {z[j]:.3f})"
            else:
                termino_str += f"(x - {z[j]:.3f})"
        
        if coef >= 0:
            terminos_latex.append(f"+ {coef:.6f} \\cdot {termino_str}")
        else:
            terminos_latex.append(f"{coef:.6f} \\cdot {termino_str}")
        
        pasos.append(f"     {terminos_latex[-1]}")

    # Simplificar polinomio
    polinomio_expandido = sp.expand(polinomio)

    pasos.append("")
    pasos.append("3. Polinomio expandido:")
    # Convertir el polinomio a LaTeX
    polinomio_latex = sp.latex(polinomio_expandido)
    pasos.append(f"$$H(x) = {polinomio_latex}$$")

    # Evaluar en x_eval
    resultado = float(polinomio_expandido.subs(x, x_eval))

    pasos.append("")
    pasos.append("4. Evaluación:")
    pasos.append(f"$$H({x_eval}) = {resultado:.8f}$$")

    return {
        'resultado': resultado,
        'polinomio': str(polinomio_expandido),
        'polinomio_latex': polinomio_latex,
        'pasos': pasos,
        'puntos': puntos
    }

def limpiar_funcion_mathlive(funcion_str):
    """
    Limpia la cadena de entrada proveniente de MathLive para que sea compatible con sympy.sympify
    """
    import re
    
    if not funcion_str:
        return ""
    
    # Eliminar espacios extra
    funcion_str = funcion_str.strip()
    
    # Conversiones básicas de LaTeX a Python
    conversiones = [
        # Funciones trigonométricas
        (r'\\sin\s*\(', 'sin('),
        (r'\\cos\s*\(', 'cos('),
        (r'\\tan\s*\(', 'tan('),
        (r'\\sec\s*\(', '1/cos('),
        (r'\\csc\s*\(', '1/sin('),
        (r'\\cot\s*\(', '1/tan('),
        
        # Funciones inversas
        (r'\\arcsin\s*\(', 'asin('),
        (r'\\arccos\s*\(', 'acos('),
        (r'\\arctan\s*\(', 'atan('),
        
        # Funciones hiperbólicas
        (r'\\sinh\s*\(', 'sinh('),
        (r'\\cosh\s*\(', 'cosh('),
        (r'\\tanh\s*\(', 'tanh('),
        
        # Funciones logarítmicas
        (r'\\ln\s*\(', 'log('),
        (r'\\log\s*\(', 'log10('),
        
        # Exponencial
        (r'\\exp\s*\(', 'exp('),
        (r'e\^', 'exp('),
        
        # Raíz cuadrada
        (r'\\sqrt\s*\{([^}]+)\}', r'sqrt(\1)'),
        (r'\\sqrt\s*\(', 'sqrt('),
        
        # Valor absoluto
        (r'\\left\|([^|]+)\\right\|', r'abs(\1)'),
        
        # Limpiar comandos LaTeX
        (r'\\left\(', '('),
        (r'\\right\)', ')'),
        (r'\\left\{', '('),
        (r'\\right\}', ')'),
        (r'\{', '('),
        (r'\}', ')'),
        
        # Potencias
        (r'\^', '**'),
        
        # Constantes matemáticas
        (r'\\pi', 'pi'),
        (r'\\e\b', 'E'),
        
        # Fracciones simples
        (r'\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}', r'(\1)/(\2)'),
        
        # Limpiar asteriscos múltiples (solo 3 o más, para no romper potencias)
        (r'\*{3,}', '*'),
        
        # Multiplicación implícita
        (r'(\d)([a-zA-Z])', r'\1*\2'),
        (r'([a-zA-Z])(\d)', r'\1*\2'),
        (r'\)\(', ')*('),
        (r'\)([a-zA-Z])', r')*\1'),
        (r'([a-zA-Z])\(', r'\1*('),
    ]
    
    # Aplicar todas las conversiones
    for patron, reemplazo in conversiones:
        funcion_str = re.sub(patron, reemplazo, funcion_str)
    
    # Limpiar espacios finales
    funcion_str = re.sub(r'\s+', '', funcion_str)
    
    return funcion_str

def integracion_compuesta(funcion_str, a, b, n, metodo):
    # Limpiar función de entrada
    funcion_str = limpiar_funcion_mathlive(funcion_str)
    
    # Parsear función
    x = symbols('x')
    try:
        # Intentar parsear la función
        funcion_sym = sympify(funcion_str)
        f = lambdify(x, funcion_sym, ['numpy', 'math'])
        
        # Crear LaTeX para mostrar
        try:
            funcion_latex = sp.latex(funcion_sym)
        except:
            funcion_latex = str(funcion_sym)
            
    except Exception as e:
        # Si falla el parsing, intentar con algunas correcciones adicionales
        try:
            # Correcciones adicionales para casos problemáticos
            funcion_corregida = funcion_str
            
            # Asegurar que las funciones matemáticas estén bien formateadas
            import re
            funcion_corregida = re.sub(r'(\w+)\*\(', r'\1(', funcion_corregida)
            
            funcion_sym = sympify(funcion_corregida)
            f = lambdify(x, funcion_sym, ['numpy', 'math'])
            funcion_latex = sp.latex(funcion_sym)
            
        except Exception as e2:
            raise ValueError(f"No se pudo parsear la función '{funcion_str}'. Error: {str(e2)}")
    
    h = (b - a) / n
    pasos = []
    
    pasos.append(f"=== INTEGRACIÓN NUMÉRICA COMPUESTA - {metodo.upper()} ===")
    pasos.append(f"Función: $$f(x) = {funcion_latex}$$")
    pasos.append(f"Intervalo: $[{a}, {b}]$")
    pasos.append(f"Número de subintervalos: $n = {n}$")
    pasos.append(f"Ancho de subintervalo: $$h = \\frac{{b-a}}{{n}} = \\frac{{{b}-{a}}}{{{n}}} = {h:.6f}$$")
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
    pasos.append("$$\\int_a^b f(x)dx \\approx \\frac{h}{2}\\left[f(x_0) + 2\\sum_{i=1}^{n-1}f(x_i) + f(x_n)\\right]$$")
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
    pasos.append(f"$$\\mathrm{{Resultado}} = \\frac{{h}}{{2}} \\times \\text{{suma}} = \\frac{{{h:.6f}}}{{2}} \\times {suma:.6f} = {resultado:.8f}$$")

    return resultado

def _simpson13_compuesto(f, a, b, n, h, pasos):
    """Regla de Simpson 1/3 compuesta"""
    pasos.append("Fórmula de Simpson 1/3 compuesta:")
    pasos.append("$$\\int_a^b f(x)dx \\approx \\frac{h}{3}\\left[f(x_0) + 4\\sum_{i=1}^{n/2}f(x_{2i-1}) + 2\\sum_{i=1}^{n/2-1}f(x_{2i}) + f(x_n)\\right]$$")
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
    pasos.append(f"$$\\mathrm{{Resultado}} = \\frac{{h}}{{3}} \\times \\text{{suma}} = \\frac{{{h:.6f}}}{{3}} \\times {suma_total:.6f} = {resultado:.8f}$$")
    
    return resultado

def _simpson38_compuesto(f, a, b, n, h, pasos):
    """Regla de Simpson 3/8 compuesta"""
    pasos.append("Fórmula de Simpson 3/8 compuesta:")
    pasos.append("$$\\int_a^b f(x)dx \\approx \\frac{3h}{8}\\left[f(x_0) + 3\\sum_{i=1}^{n/3}f(x_{3i-2}) + 3\\sum_{i=1}^{n/3}f(x_{3i-1}) + 2\\sum_{i=1}^{n/3-1}f(x_{3i}) + f(x_n)\\right]$$")
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
    pasos.append(f"$$\\mathrm{{Resultado}} = \\frac{{3h}}{{8}} \\times \\text{{suma}} = \\frac{{3\\times{h:.6f}}}{{8}} \\times {suma_total:.6f} = {resultado:.8f}$$")
    
    return resultado

def generar_datos_grafica_hermite(puntos, polinomio_str, x_eval):
    """
    Genera datos para la gráfica de interpolación de Hermite
    """
    import numpy as np
    from sympy import symbols, sympify, lambdify
    
    try:
        # Extraer coordenadas de los puntos
        x_vals = [p[0] for p in puntos]
        f_vals = [p[1] for p in puntos]
        df_vals = [p[2] for p in puntos]
        
        # Determinar rango para la gráfica
        x_min = min(x_vals) - 1
        x_max = max(x_vals) + 1
        
        # Crear puntos para evaluar el polinomio (curva suave)
        x_curve = np.linspace(x_min, x_max, 200)
        
        # Convertir polinomio a función evaluable
        x = symbols('x')
        polinomio_sym = sympify(polinomio_str)
        f_poly = lambdify(x, polinomio_sym, 'numpy')
        
        # Evaluar polinomio
        y_curve = f_poly(x_curve)
        
        # Punto de evaluación
        y_eval = f_poly(x_eval)
        
        return {
            'puntos_x': x_vals,
            'puntos_y': f_vals,
            'derivadas': df_vals,
            'curva_x': x_curve.tolist(),
            'curva_y': y_curve.tolist(),
            'eval_x': x_eval,
            'eval_y': float(y_eval),
            'x_min': float(x_min),
            'x_max': float(x_max),
            'y_min': float(min(min(f_vals), min(y_curve)) - 1),
            'y_max': float(max(max(f_vals), max(y_curve)) + 1)
        }
    except Exception as e:
        return None

def generar_datos_grafica_integracion(funcion_str, a, b, n, metodo, resultado):
    """
    Genera datos para la gráfica de integración numérica
    """
    import numpy as np
    from sympy import symbols, sympify, lambdify
    
    try:
        # Limpiar y parsear función
        funcion_str = limpiar_funcion_mathlive(funcion_str)
        x = symbols('x')
        funcion_sym = sympify(funcion_str)
        f = lambdify(x, funcion_sym, 'numpy')
        
        # Puntos para la curva suave de la función
        x_curve = np.linspace(a - 0.5, b + 0.5, 300)
        y_curve = f(x_curve)
        
        # Puntos para el área de integración
        x_area = np.linspace(a, b, 100)
        y_area = f(x_area)
        
        # Puntos de los subintervalos según el método
        h = (b - a) / n
        x_intervals = [a + i * h for i in range(n + 1)]
        y_intervals = [f(x) for x in x_intervals]
        
        # Datos específicos del método
        if metodo == 'trapecio':
            # Líneas de los trapecios
            trap_x = []
            trap_y = []
            for i in range(n):
                trap_x.extend([x_intervals[i], x_intervals[i+1], x_intervals[i+1], x_intervals[i], x_intervals[i], None])
                trap_y.extend([0, 0, y_intervals[i+1], y_intervals[i], 0, None])
        else:
            trap_x = []
            trap_y = []
        
        return {
            'curva_x': x_curve.tolist(),
            'curva_y': y_curve.tolist(),
            'area_x': x_area.tolist(),
            'area_y': y_area.tolist(),
            'intervalos_x': x_intervals,
            'intervalos_y': y_intervals,
            'trapecio_x': trap_x,
            'trapecio_y': trap_y,
            'a': a,
            'b': b,
            'resultado': resultado,
            'metodo': metodo,
            'n': n,
            'h': h
        }
    except Exception as e:
        return None

def generar_datos_grafica_simplex(funcion_objetivo, restricciones, solucion, nombres_variables, tipo_optimizacion):
    """
    Genera datos para la gráfica del método Simplex (solo para 2 variables)
    """
    import numpy as np
    
    try:
        # Solo funciona para 2 variables
        if len(funcion_objetivo) != 2:
            return None
            
        # Coeficientes de la función objetivo
        c1, c2 = funcion_objetivo[0], funcion_objetivo[1]
        
        # Determinar rango de la gráfica
        x_max = 10
        y_max = 10
        
        # Ajustar rango basado en restricciones
        for rest in restricciones:
            if rest['valor'] > 0:
                if rest['coeficientes'][0] > 0:
                    x_max = max(x_max, rest['valor'] / rest['coeficientes'][0] + 2)
                if rest['coeficientes'][1] > 0:
                    y_max = max(y_max, rest['valor'] / rest['coeficientes'][1] + 2)
        
        x_max = min(x_max, 20)  # Limitar el rango máximo
        y_max = min(y_max, 20)
        
        # Generar puntos para las líneas de restricción
        x_line = np.linspace(0, x_max, 100)
        
        restricciones_data = []
        vertices_factibles = [(0, 0)]  # Siempre incluir el origen
        
        # Procesar cada restricción
        for i, rest in enumerate(restricciones):
            a1, a2 = rest['coeficientes'][0], rest['coeficientes'][1]
            b = rest['valor']
            tipo = rest['tipo']
            
            # Calcular línea de restricción: a1*x + a2*y = b
            if a2 != 0:
                y_line = (b - a1 * x_line) / a2
                # Filtrar valores negativos
                valid_indices = (y_line >= 0) & (x_line >= 0)
                x_valid = x_line[valid_indices]
                y_valid = y_line[valid_indices]
            else:
                # Línea vertical
                if a1 != 0:
                    x_vert = b / a1
                    x_valid = [x_vert, x_vert]
                    y_valid = [0, y_max]
                else:
                    continue
            
            restricciones_data.append({
                'x': x_valid.tolist() if hasattr(x_valid, 'tolist') else x_valid,
                'y': y_valid.tolist() if hasattr(y_valid, 'tolist') else y_valid,
                'nombre': f'Restricción {i+1}: {a1:.1f}x₁ + {a2:.1f}x₂ {tipo} {b:.1f}',
                'tipo': tipo,
                'coeficientes': [a1, a2],
                'valor': b
            })
            
            # Encontrar intersecciones con los ejes
            if a1 != 0 and b/a1 >= 0:
                vertices_factibles.append((b/a1, 0))
            if a2 != 0 and b/a2 >= 0:
                vertices_factibles.append((0, b/a2))
        
        # Encontrar intersecciones entre restricciones
        for i in range(len(restricciones)):
            for j in range(i+1, len(restricciones)):
                rest1 = restricciones[i]
                rest2 = restricciones[j]
                
                a1, a2, b1 = rest1['coeficientes'][0], rest1['coeficientes'][1], rest1['valor']
                c1, c2, b2 = rest2['coeficientes'][0], rest2['coeficientes'][1], rest2['valor']
                
                # Resolver sistema 2x2
                det = a1*c2 - a2*c1
                if abs(det) > 1e-10:  # No son paralelas
                    x_int = (b1*c2 - b2*a2) / det
                    y_int = (a1*b2 - c1*b1) / det
                    
                    if x_int >= 0 and y_int >= 0:
                        vertices_factibles.append((x_int, y_int))
        
        # Filtrar vértices que satisfacen todas las restricciones
        vertices_validos = []
        for x, y in vertices_factibles:
            valido = True
            for rest in restricciones:
                a1, a2 = rest['coeficientes'][0], rest['coeficientes'][1]
                valor_rest = a1*x + a2*y
                
                if rest['tipo'] == '<=':
                    if valor_rest > rest['valor'] + 1e-10:
                        valido = False
                        break
                elif rest['tipo'] == '>=':
                    if valor_rest < rest['valor'] - 1e-10:
                        valido = False
                        break
                else:  # '='
                    if abs(valor_rest - rest['valor']) > 1e-10:
                        valido = False
                        break
            
            if valido:
                vertices_validos.append((x, y))
        
        # Eliminar duplicados
        vertices_unicos = []
        for v in vertices_validos:
            es_duplicado = False
            for vu in vertices_unicos:
                if abs(v[0] - vu[0]) < 1e-6 and abs(v[1] - vu[1]) < 1e-6:
                    es_duplicado = True
                    break
            if not es_duplicado:
                vertices_unicos.append(v)
        
        # Ordenar vértices para formar el polígono convexo
        if len(vertices_unicos) > 2:
            # Encontrar el centroide
            cx = sum(v[0] for v in vertices_unicos) / len(vertices_unicos)
            cy = sum(v[1] for v in vertices_unicos) / len(vertices_unicos)
            
            # Ordenar por ángulo respecto al centroide
            import math
            def angulo(v):
                return math.atan2(v[1] - cy, v[0] - cx)
            
            vertices_unicos.sort(key=angulo)
        
        # Líneas de la función objetivo
        if c2 != 0:
            # Diferentes valores de Z para mostrar la dirección de optimización
            z_values = []
            if solucion:
                z_optimo = c1 * solucion[0] + c2 * solucion[1]
                z_values = [z_optimo * 0.5, z_optimo * 0.75, z_optimo]
            else:
                z_values = [5, 10, 15]
            
            objetivo_lines = []
            for z in z_values:
                y_obj = (z - c1 * x_line) / c2
                valid_obj = (y_obj >= 0) & (x_line >= 0) & (y_obj <= y_max)
                objetivo_lines.append({
                    'x': x_line[valid_obj].tolist(),
                    'y': y_obj[valid_obj].tolist(),
                    'z': z,
                    'es_optimo': abs(z - (z_values[-1] if z_values else 0)) < 1e-6
                })
        else:
            objetivo_lines = []
        
        return {
            'restricciones': restricciones_data,
            'vertices_factibles': vertices_unicos,
            'objetivo_lines': objetivo_lines,
            'punto_optimo': {
                'x': solucion[0] if solucion else 0,
                'y': solucion[1] if solucion else 0,
                'z': c1 * solucion[0] + c2 * solucion[1] if solucion else 0
            },
            'rango': {
                'x_max': x_max,
                'y_max': y_max
            },
            'funcion_objetivo': {
                'c1': c1,
                'c2': c2,
                'ecuacion': f'{c1:.2f}x₁ + {c2:.2f}x₂'
            },
            'nombres_variables': nombres_variables,
            'tipo_optimizacion': tipo_optimizacion
        }
        
    except Exception as e:
        print(f"Error generando datos de gráfica: {e}")
        return None

def preparar_problema_simplex(c, restricciones, tipo, nombres_variables, pasos):
    """Convierte el problema a forma estándar para el método Simplex"""
    
    pasos.append("1. PREPARACIÓN DEL PROBLEMA")
    pasos.append("")
    pasos.append("📋 PROBLEMA ORIGINAL:")
    
    # Mostrar función objetivo
    if tipo == 'maximizar':
        pasos.append(f"   Maximizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
    else:
        pasos.append(f"   Minimizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
    
    pasos.append("   Sujeto a:")
    for i, rest in enumerate(restricciones):
        coef_str = " + ".join([f"{rest['coeficientes'][j]:.3f}·{nombres_variables[j]}" for j in range(len(rest['coeficientes']))])
        pasos.append(f"      {coef_str} {rest['tipo']} {rest['valor']:.3f}")
    
    pasos.append(f"      {', '.join(nombres_variables)} ≥ 0")
    pasos.append("")
    
    # Detectar si necesitamos el método de la Gran M
    necesita_gran_m = any(rest['tipo'] in ['>=', '='] for rest in restricciones)
    
    if necesita_gran_m:
        pasos.append("🔍 DETECCIÓN DEL MÉTODO:")
        pasos.append("   Se detectaron restricciones de tipo ≥ o =")
        pasos.append("   ➡️ Se aplicará el MÉTODO DE LA GRAN M")
        pasos.append("")
    else:
        pasos.append("🔍 DETECCIÓN DEL MÉTODO:")
        pasos.append("   Todas las restricciones son de tipo ≤")
        pasos.append("   ➡️ Se aplicará el MÉTODO SIMPLEX ESTÁNDAR")
        pasos.append("")
    
    # Convertir a forma estándar
    pasos.append("🔄 CONVERSIÓN A FORMA ESTÁNDAR:")
    pasos.append("")
    
    A = []
    b = []
    variables_basicas = []
    variables_artificiales = []
    num_vars_originales = len(c)
    contador_slack = 1
    contador_surplus = 1
    contador_artificial = 1
    
    # Procesar restricciones
    for i, rest in enumerate(restricciones):
        fila = rest['coeficientes'][:]
        
        if rest['tipo'] == '<=':
            # Agregar variable de holgura
            var_slack = f"s{contador_slack}"
            variables_basicas.append(var_slack)
            contador_slack += 1
            pasos.append(f"   Restricción {i+1}: Agregar variable de holgura {var_slack}")
            
        elif rest['tipo'] == '>=':
            # Agregar variable de exceso y artificial
            var_surplus = f"e{contador_surplus}"
            var_artificial = f"a{contador_artificial}"
            variables_basicas.append(var_artificial)
            variables_artificiales.append(var_artificial)
            contador_surplus += 1
            contador_artificial += 1
            pasos.append(f"   Restricción {i+1}: Agregar variable de exceso {var_surplus} y artificial {var_artificial}")
            
        else:  # '='
            # Agregar variable artificial
            var_artificial = f"a{contador_artificial}"
            variables_basicas.append(var_artificial)
            variables_artificiales.append(var_artificial)
            contador_artificial += 1
            pasos.append(f"   Restricción {i+1}: Agregar variable artificial {var_artificial}")
        
        A.append(fila)
        b.append(rest['valor'])
    
    # Completar matriz A con variables de holgura/exceso/artificiales
    num_restricciones = len(restricciones)
    num_vars_slack = contador_slack - 1
    num_vars_surplus = contador_surplus - 1
    num_vars_artificial = contador_artificial - 1
    
    total_vars = num_vars_originales + num_vars_slack + num_vars_surplus + num_vars_artificial
    
    # Expandir matriz A
    for i in range(num_restricciones):
        # Agregar ceros para las variables adicionales
        while len(A[i]) < total_vars:
            A[i].append(0.0)
    
    # Llenar las columnas de variables de holgura/exceso/artificiales
    col_actual = num_vars_originales
    contador_slack = 1
    contador_surplus = 1
    contador_artificial = 1
    
    for i, rest in enumerate(restricciones):
        if rest['tipo'] == '<=':
            A[i][col_actual] = 1.0  # Variable de holgura
            col_actual += 1
            
        elif rest['tipo'] == '>=':
            A[i][col_actual] = -1.0  # Variable de exceso
            A[i][col_actual + 1] = 1.0  # Variable artificial
            col_actual += 2
            
        else:  # '='
            A[i][col_actual] = 1.0  # Variable artificial
            col_actual += 1
    
    # Extender función objetivo
    c_extendida = c[:]
    
    # Agregar ceros para variables de holgura y exceso
    for _ in range(num_vars_slack + num_vars_surplus):
        c_extendida.append(0.0)
    
    # Valor de la Gran M
    M = 1000000
    
    # Agregar penalización para variables artificiales (Gran M)
    for _ in range(num_vars_artificial):
        if tipo == 'maximizar':
            c_extendida.append(-M)  # Gran penalización negativa para maximización
        else:
            c_extendida.append(M)   # Gran penalización positiva para minimización
    
    if necesita_gran_m:
        pasos.append("")
        pasos.append("📊 MÉTODO DE LA GRAN M:")
        pasos.append(f"   Valor de M utilizado: {M:,}")
        pasos.append("   Variables artificiales penalizadas:")
        for var_art in variables_artificiales:
            if tipo == 'maximizar':
                pasos.append(f"      {var_art}: coeficiente = -M = -{M:,}")
            else:
                pasos.append(f"      {var_art}: coeficiente = +M = +{M:,}")
    
    pasos.append("")
    pasos.append("✅ FORMA ESTÁNDAR OBTENIDA:")
    
    # Mostrar función objetivo con M simbólica para mejor comprensión
    obj_str_parts = []
    for i in range(len(c_extendida)):
        coef = c_extendida[i]
        if i < num_vars_originales:
            var_name = nombres_variables[i]
        elif i < num_vars_originales + num_vars_slack:
            var_name = f"s{i - num_vars_originales + 1}"
        elif i < num_vars_originales + num_vars_slack + num_vars_surplus:
            var_name = f"e{i - num_vars_originales - num_vars_slack + 1}"
        else:
            var_name = f"a{i - num_vars_originales - num_vars_slack - num_vars_surplus + 1}"
            # Mostrar M simbólicamente
            if abs(coef) == M:
                if coef > 0:
                    obj_str_parts.append(f"+M·{var_name}")
                else:
                    obj_str_parts.append(f"-M·{var_name}")
                continue
        
        if coef != 0:
            if coef > 0 and obj_str_parts:
                obj_str_parts.append(f"+{coef:.3f}·{var_name}")
            else:
                obj_str_parts.append(f"{coef:.3f}·{var_name}")
    
    if tipo == 'maximizar':
        pasos.append("   Maximizar: Z = " + "".join(obj_str_parts))
    else:
        pasos.append("   Minimizar: Z = " + "".join(obj_str_parts))
    
    pasos.append("   Sujeto a:")
    for i in range(len(A)):
        coef_parts = []
        for j in range(len(A[i])):
            coef = A[i][j]
            if j < num_vars_originales:
                var_name = nombres_variables[j]
            elif j < num_vars_originales + num_vars_slack:
                var_name = f"s{j - num_vars_originales + 1}"
            elif j < num_vars_originales + num_vars_slack + num_vars_surplus:
                var_name = f"e{j - num_vars_originales - num_vars_slack + 1}"
            else:
                var_name = f"a{j - num_vars_originales - num_vars_slack - num_vars_surplus + 1}"
            
            if coef != 0:
                if coef > 0 and coef_parts:
                    coef_parts.append(f"+{coef:.3f}·{var_name}")
                else:
                    coef_parts.append(f"{coef:.3f}·{var_name}")
        
        pasos.append(f"      {''.join(coef_parts)} = {b[i]:.3f}")
    pasos.append("")
    
    return {
        'A': A,
        'b': b,
        'c': c_extendida,
        'variables_basicas': variables_basicas,
        'variables_artificiales': variables_artificiales,
        'num_vars_originales': num_vars_originales,
        'tipo_original': tipo,
        'nombres_variables': nombres_variables,
        'necesita_gran_m': necesita_gran_m,
        'M': M
    }

def metodo_simplex(problema, pasos):
    """Resuelve el problema usando el algoritmo Simplex con soporte para Gran M"""
    
    A = problema['A']
    b = problema['b']
    c = problema['c']
    variables_basicas = problema['variables_basicas']
    variables_artificiales = problema.get('variables_artificiales', [])
    num_vars_originales = problema['num_vars_originales']
    tipo_original = problema['tipo_original']
    nombres_variables = problema['nombres_variables']
    necesita_gran_m = problema.get('necesita_gran_m', False)
    M = problema.get('M', 1000000)
    
    m = len(A)  # número de restricciones
    n = len(c)  # número de variables
    
    pasos.append("2. APLICACIÓN DEL MÉTODO SIMPLEX")
    if necesita_gran_m:
        pasos.append("   (Utilizando el Método de la Gran M)")
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
    
    # Si usamos Gran M, necesitamos eliminar las variables artificiales de la función objetivo
    if necesita_gran_m and variables_artificiales:
        pasos.append("🔧 ELIMINACIÓN DE VARIABLES ARTIFICIALES DE LA FUNCIÓN OBJETIVO:")
        pasos.append("   (Operaciones iniciales para el método de la Gran M)")
        pasos.append("")
        
        # Para cada variable artificial en la base, eliminarla de la función objetivo
        for i, var_basica in enumerate(variables_basicas):
            if var_basica in variables_artificiales:
                # Encontrar la columna de esta variable artificial
                col_artificial = -1
                
                # Buscar la columna que corresponde a esta variable artificial
                for j in range(n):
                    # Verificar si esta columna tiene 1 en la fila i y 0 en las demás filas de restricción
                    es_columna_basica = True
                    for k in range(m):
                        if k == i and abs(tabla[k][j] - 1.0) > 1e-10:
                            es_columna_basica = False
                            break
                        elif k != i and abs(tabla[k][j]) > 1e-10:
                            es_columna_basica = False
                            break
                    
                    if es_columna_basica and abs(tabla[-1][j]) > 1e-10:
                        col_artificial = j
                        break
                
                if col_artificial >= 0:
                    # Eliminar la variable artificial de la función objetivo
                    coef_obj = tabla[-1][col_artificial]
                    pasos.append(f"   Eliminando {var_basica} de la función objetivo:")
                    pasos.append(f"   Fila objetivo = Fila objetivo - ({coef_obj:.6f}) × Fila {i+1}")
                    
                    for j in range(len(tabla[-1])):
                        tabla[-1][j] -= coef_obj * tabla[i][j]
    
    iteracion = 0
    tablas_simplex = []
    
    # Variables para rastrear pivotes
    historial_pivotes = []
    
    while True:
        iteracion += 1
        pasos.append(f"ITERACIÓN {iteracion}")
        pasos.append("")
        
        # Mostrar tabla actual
        tabla_info = _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos, nombres_variables, num_vars_originales)
        tablas_simplex.append(tabla_info)
        
        # Verificar optimalidad
        fila_obj_actual = tabla[-1][:-1]
        if all(coef >= -1e-10 for coef in fila_obj_actual):  # Usar tolerancia numérica
            pasos.append("✓ Todos los coeficientes en la fila objetivo son ≥ 0")
            
            # Verificar si hay variables artificiales en la solución final
            if necesita_gran_m:
                variables_artificiales_en_solucion = []
                for i, var in enumerate(variables_basicas):
                    if var in variables_artificiales and abs(tabla[i][-1]) > 1e-10:
                        variables_artificiales_en_solucion.append((var, tabla[i][-1]))
                
                if variables_artificiales_en_solucion:
                    pasos.append("")
                    pasos.append("❌ PROBLEMA SIN SOLUCIÓN FACTIBLE")
                    pasos.append("   Variables artificiales con valor no cero en la solución:")
                    for var, valor in variables_artificiales_en_solucion:
                        pasos.append(f"      {var} = {valor:.6f}")
                    pasos.append("")
                    pasos.append("🔍 INTERPRETACIÓN:")
                    pasos.append("   - El problema original no tiene solución factible")
                    pasos.append("   - Las restricciones son inconsistentes")
                    pasos.append("   - No existe ningún punto que satisfaga todas las restricciones")
                    
                    return {
                        'error': 'Problema sin solución factible - Las restricciones son inconsistentes',
                        'pasos': pasos,
                        'tablas': tablas_simplex,
                        'interpretacion': 'Las restricciones del problema son inconsistentes',
                        'sugerencia': 'Revise las restricciones del problema para asegurar que sean consistentes'
                    }
                else:
                    pasos.append("✓ Todas las variables artificiales tienen valor cero")
            
            pasos.append("¡SOLUCIÓN ÓPTIMA ENCONTRADA!")
            break
        
        # Encontrar variable entrante (columna pivote)
        col_pivote = min(range(len(fila_obj_actual)), key=lambda i: fila_obj_actual[i])
        coef_entrante = fila_obj_actual[col_pivote]
        
        # Determinar nombre de variable entrante
        if col_pivote < num_vars_originales:
            var_entrante = nombres_variables[col_pivote]
        else:
            # Determinar el tipo de variable no original
            idx_no_original = col_pivote - num_vars_originales
            var_entrante = f"var_{col_pivote + 1}"
        
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
    solucion_con_nombres = {}
    
    for i, var in enumerate(variables_basicas):
        # Buscar si es una variable original
        for j, nombre_var in enumerate(nombres_variables):
            if var == nombre_var:
                solucion[j] = tabla[i][-1]
                solucion_con_nombres[nombre_var] = tabla[i][-1]
                break
    
    valor_objetivo = tabla[-1][-1]
    # Mostrar siempre el valor óptimo como positivo
    valor_objetivo_mostrar = abs(valor_objetivo)
    if tipo_original == 'minimizar':
        valor_objetivo = -valor_objetivo
        valor_objetivo_mostrar = abs(valor_objetivo)

    pasos.append("")
    pasos.append("3. SOLUCIÓN ÓPTIMA")
    pasos.append("")
    
    if necesita_gran_m:
        pasos.append("🎯 MÉTODO DE LA GRAN M - SOLUCIÓN FINAL:")
        pasos.append("")
    
    pasos.append("📋 VARIABLES DE DECISIÓN:")
    for i, (nombre, val) in enumerate(zip(nombres_variables, solucion)):
        pasos.append(f"   {nombre} = {val:.6f}")
    
    pasos.append("")
    pasos.append("📊 VARIABLES DE HOLGURA/EXCESO:")
    for i, var in enumerate(variables_basicas):
        if var not in nombres_variables and var not in variables_artificiales:
            pasos.append(f"   {var} = {tabla[i][-1]:.6f}")
    
    if necesita_gran_m and variables_artificiales:
        pasos.append("")
        pasos.append("🚫 VARIABLES ARTIFICIALES (deben ser cero):")
        for i, var in enumerate(variables_basicas):
            if var in variables_artificiales:
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
        'solucion_con_nombres': solucion_con_nombres,
        'nombres_variables': nombres_variables,
        'valor_objetivo': valor_objetivo_mostrar,
        'pasos': pasos,
        'tablas': tablas_simplex,
        'variables_basicas': variables_basicas,
        'tipo_optimizacion': tipo_original,
        'historial_pivotes': historial_pivotes,
        'metodo_usado': 'Gran M' if necesita_gran_m else 'Simplex Estándar'
    }

def _mostrar_tabla_simplex(tabla, variables_basicas, iteracion, pasos, nombres_variables, num_vars_originales):
    """Muestra la tabla Simplex de manera formateada con HTML"""
    
    m = len(tabla) - 1  # número de restricciones
    n = len(tabla[0]) - 1  # número de variables
    
    pasos.append("📋 TABLA SIMPLEX:")
    pasos.append("")
    
    # Crear tabla HTML con estilos mejorados
    tabla_html = '<div class="simplex-table-container">'
    tabla_html += f'<div class="table-title">Iteración {iteracion}</div>'
    tabla_html += '<table class="simplex-table table table-bordered table-hover">'
    
    # Encabezado
    tabla_html += '<thead class="table-dark"><tr>'
    tabla_html += '<th class="base-header text-center">Base</th>'
    for j in range(n):
        if j < num_vars_originales:
            tabla_html += f'<th class="var-header text-center">{nombres_variables[j]}</th>'
        else:
            tabla_html += f'<th class="slack-header text-center">s<sub>{j-num_vars_originales+1}</sub></th>'
    tabla_html += '<th class="rhs-header text-center">b(i)</th>'
    tabla_html += '</tr></thead>'
    
    # Cuerpo de la tabla
    tabla_html += '<tbody>'
    
    # Filas de restricciones
    for i in range(m):
        tabla_html += f'<tr class="constraint-row" data-row="{i}">'
        tabla_html += f'<td class="base-column text-center fw-bold">{variables_basicas[i]}</td>'
        for j in range(len(tabla[i])):
            valor = tabla[i][j]
            clase_celda = f'data-cell text-center data-row-{i} data-col-{j}'
            if j == len(tabla[i]) - 1:  # RHS column
                clase_celda += ' rhs-cell fw-bold'
            tabla_html += f'<td class="{clase_celda}">{valor:.4f}</td>'
        tabla_html += '</tr>'
    
    # Fila objetivo
    tabla_html += '<tr class="objective-row table-info">'
    tabla_html += '<td class="base-column objective-label text-center fw-bold">Z</td>'
    for j in range(len(tabla[-1])):
        valor = tabla[-1][j]
        clase_celda = f'objective-cell text-center data-col-{j}'
        if j == len(tabla[-1]) - 1:  # RHS column (valor de Z)
            clase_celda += ' objective-value fw-bold'
        tabla_html += f'<td class="{clase_celda}">{valor:.4f}</td>'
    tabla_html += '</tr>'
    
    tabla_html += '</tbody></table>'
    
    tabla_html += '</div>'
    
    pasos.append(tabla_html)
    pasos.append("")
    
    return {
        'iteracion': iteracion,
        'tabla': [fila[:] for fila in tabla],  # Copia profunda
        'variables_basicas': variables_basicas[:],
        'tabla_html': tabla_html
    }
