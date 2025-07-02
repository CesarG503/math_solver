import numpy as np
import sympy as sp
from sympy import symbols, lambdify, sympify
import math
from fractions import Fraction

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

# ==================== CLASES PARA MÉTODOS SIMPLEX ====================

class SimplexEstandar:
    """Clase para resolver problemas de programación lineal usando el método Simplex estándar"""
    
    def __init__(self):
        self.iteracion = 0
        self.pasos = []
        self.tablas = []
        
    def resolver(self, funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables):
        """Resuelve un problema usando el método Simplex estándar (solo restricciones <=)"""
        
        self.pasos = []
        self.tablas = []
        self.iteracion = 0
        
        # Verificar que todas las restricciones sean <=
        for rest in restricciones:
            if rest['tipo'] != '<=':
                raise ValueError("El método Simplex estándar solo acepta restricciones <=")
        
        # Preparar problema
        problema = self._preparar_problema_estandar(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables)
        
        # Resolver
        return self._resolver_simplex_estandar(problema)
    
    def _preparar_problema_estandar(self, c, restricciones, tipo, nombres_variables):
        """Prepara el problema para el método Simplex estándar"""
        
        self.pasos.append("1. PREPARACIÓN DEL PROBLEMA - MÉTODO SIMPLEX ESTÁNDAR")
        self.pasos.append("")
        self.pasos.append("📋 PROBLEMA ORIGINAL:")
        
        # Mostrar función objetivo
        if tipo == 'maximizar':
            self.pasos.append(f"   Maximizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
        else:
            self.pasos.append(f"   Minimizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
        
        self.pasos.append("   Sujeto a:")
        for i, rest in enumerate(restricciones):
            coef_str = " + ".join([f"{rest['coeficientes'][j]:.3f}·{nombres_variables[j]}" for j in range(len(rest['coeficientes']))])
            self.pasos.append(f"      {coef_str} ≤ {rest['valor']:.3f}")
        
        self.pasos.append(f"      {', '.join(nombres_variables)} ≥ 0")
        self.pasos.append("")
        
        self.pasos.append("🔍 DETECCIÓN DEL MÉTODO:")
        self.pasos.append("   Todas las restricciones son de tipo ≤")
        self.pasos.append("   ➡️ Se aplicará el MÉTODO SIMPLEX ESTÁNDAR")
        self.pasos.append("")
        
        # Convertir a forma estándar
        self.pasos.append("🔄 CONVERSIÓN A FORMA ESTÁNDAR:")
        self.pasos.append("")
        
        A = []
        b = []
        variables_basicas = []
        num_vars_originales = len(c)
        contador_slack = 1
        
        # Procesar restricciones (agregar variables de holgura)
        for i, rest in enumerate(restricciones):
            fila = rest['coeficientes'][:]
            var_slack = f"s{contador_slack}"
            variables_basicas.append(var_slack)
            contador_slack += 1
            self.pasos.append(f"   Restricción {i+1}: Agregar variable de holgura {var_slack}")
            
            A.append(fila)
            b.append(rest['valor'])
        
        # Completar matriz A con variables de holgura
        num_restricciones = len(restricciones)
        num_vars_slack = contador_slack - 1
        total_vars = num_vars_originales + num_vars_slack
        
        # Expandir matriz A
        for i in range(num_restricciones):
            while len(A[i]) < total_vars:
                A[i].append(0.0)
        
        # Llenar las columnas de variables de holgura
        for i in range(num_restricciones):
            A[i][num_vars_originales + i] = 1.0  # Variable de holgura
        
        # Extender función objetivo
        c_extendida = c[:]
        for _ in range(num_vars_slack):
            c_extendida.append(0.0)  # Variables de holgura tienen coeficiente 0
        
        self.pasos.append("")
        self.pasos.append("✅ FORMA ESTÁNDAR OBTENIDA:")
        
        # Mostrar función objetivo extendida
        obj_str_parts = []
        for i in range(len(c_extendida)):
            coef = c_extendida[i]
            if i < num_vars_originales:
                var_name = nombres_variables[i]
            else:
                var_name = f"s{i - num_vars_originales + 1}"
            
            if coef != 0:
                if coef > 0 and obj_str_parts:
                    obj_str_parts.append(f"+{coef:.3f}·{var_name}")
                else:
                    obj_str_parts.append(f"{coef:.3f}·{var_name}")
        
        if tipo == 'maximizar':
            self.pasos.append("   Maximizar: Z = " + "".join(obj_str_parts))
        else:
            self.pasos.append("   Minimizar: Z = " + "".join(obj_str_parts))
        
        self.pasos.append("   Sujeto a:")
        for i in range(len(A)):
            coef_parts = []
            for j in range(len(A[i])):
                coef = A[i][j]
                if j < num_vars_originales:
                    var_name = nombres_variables[j]
                else:
                    var_name = f"s{j - num_vars_originales + 1}"
                
                if coef != 0:
                    if coef > 0 and coef_parts:
                        coef_parts.append(f"+{coef:.3f}·{var_name}")
                    else:
                        coef_parts.append(f"{coef:.3f}·{var_name}")
            
            self.pasos.append(f"      {''.join(coef_parts)} = {b[i]:.3f}")
        self.pasos.append("")
        
        return {
            'A': A,
            'b': b,
            'c': c_extendida,
            'variables_basicas': variables_basicas,
            'num_vars_originales': num_vars_originales,
            'tipo_original': tipo,
            'nombres_variables': nombres_variables,
            'necesita_gran_m': False
        }
    
    def _resolver_simplex_estandar(self, problema):
        """Resuelve usando el algoritmo Simplex estándar"""
        
        A = problema['A']
        b = problema['b']
        c = problema['c']
        variables_basicas = problema['variables_basicas']
        num_vars_originales = problema['num_vars_originales']
        tipo_original = problema['tipo_original']
        nombres_variables = problema['nombres_variables']
        
        m = len(A)  # número de restricciones
        n = len(c)  # número de variables
        
        self.pasos.append("2. APLICACIÓN DEL MÉTODO SIMPLEX ESTÁNDAR")
        self.pasos.append("")
        
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
        
        self.iteracion = 0
        max_iterations = 50
        
        while self.iteracion < max_iterations:
            self.iteracion += 1
            self.pasos.append(f"ITERACIÓN {self.iteracion}")
            self.pasos.append("")
            
            # Mostrar tabla actual
            tabla_info = self._mostrar_tabla_simplex_estandar(tabla, variables_basicas, nombres_variables, num_vars_originales)
            self.tablas.append(tabla_info)
            
            # Verificar optimalidad
            fila_obj_actual = tabla[-1][:-1]
            if all(coef >= -1e-10 for coef in fila_obj_actual):
                self.pasos.append("✓ Todos los coeficientes en la fila objetivo son ≥ 0")
                self.pasos.append("¡SOLUCIÓN ÓPTIMA ENCONTRADA!")
                break
            
            # Encontrar variable entrante (columna pivote)
            col_pivote = min(range(len(fila_obj_actual)), key=lambda i: fila_obj_actual[i])
            coef_entrante = fila_obj_actual[col_pivote]
            
            # Determinar nombre de variable entrante
            if col_pivote < num_vars_originales:
                var_entrante = nombres_variables[col_pivote]
            else:
                var_entrante = f"s{col_pivote - num_vars_originales + 1}"
            
            self.pasos.append(f"🔵 VARIABLE ENTRANTE: {var_entrante} (columna {col_pivote + 1})")
            self.pasos.append(f"   Coeficiente más negativo: {coef_entrante:.6f}")
            self.pasos.append("")
            
            # Encontrar variable saliente (fila pivote) usando prueba de razón mínima
            self.pasos.append("📊 PRUEBA DE RAZÓN MÍNIMA:")
            self.pasos.append("   Fila | Variable Base | b(i) | Coef. Columna | Razón")
            self.pasos.append("   " + "-" * 55)
            
            razones = []
            razones_validas = []
            
            for i in range(m):
                coef_col = tabla[i][col_pivote]
                rhs = tabla[i][-1]
                
                if coef_col > 1e-10:
                    razon = rhs / coef_col
                    razones.append((razon, i))
                    razones_validas.append(razon)
                    self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | {razon:7.3f}")
                else:
                    razones.append((float('inf'), i))
                    if coef_col <= -1e-10:
                        self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | No válida (≤0)")
                    else:
                        self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs:7.3f} | {coef_col:11.6f} | No válida (≈0)")
            
            self.pasos.append("")
            
            if not razones_validas or all(r == float('inf') for r, _ in razones):
                self.pasos.append("❌ SOLUCIÓN NO ACOTADA")
                self.pasos.append("   Todos los coeficientes de la columna entrante son ≤ 0")
                return {
                    'error': 'Solución no acotada - La función objetivo puede crecer indefinidamente',
                    'pasos': self.pasos,
                    'tablas': self.tablas,
                    'metodo_usado': 'Simplex Estándar'
                }
            
            razon_min, fila_pivote = min(razones)
            var_saliente = variables_basicas[fila_pivote]
            
            self.pasos.append(f"🔴 VARIABLE SALIENTE: {var_saliente} (fila {fila_pivote + 1})")
            self.pasos.append(f"   Razón mínima: {razon_min:.6f}")
            self.pasos.append("")
            
            # Elemento pivote
            pivote = tabla[fila_pivote][col_pivote]
            self.pasos.append(f"⚡ ELEMENTO PIVOTE: {pivote:.6f}")
            self.pasos.append(f"   Posición: Fila {fila_pivote + 1}, Columna {col_pivote + 1}")
            self.pasos.append("")
            
            # Actualizar la tabla anterior con información de pivote
            if self.tablas:
                self.tablas[-1]['fila_pivote'] = fila_pivote
                self.tablas[-1]['col_pivote'] = col_pivote
                self.tablas[-1]['var_entrante'] = var_entrante
                self.tablas[-1]['var_saliente'] = var_saliente
                self.tablas[-1]['elemento_pivote'] = pivote
            
            # Operaciones de pivoteo
            self.pasos.append("🔧 OPERACIONES DE PIVOTEO:")
            self.pasos.append("")
            
            # Normalizar fila pivote
            self.pasos.append(f"1️⃣ NORMALIZAR FILA PIVOTE (Fila {fila_pivote + 1}):")
            self.pasos.append(f"   Nueva Fila {fila_pivote + 1} = Fila {fila_pivote + 1} ÷ {pivote:.6f}")
            self.pasos.append("")
            
            for j in range(len(tabla[fila_pivote])):
                tabla[fila_pivote][j] /= pivote
            
            # Eliminar en otras filas
            self.pasos.append("2️⃣ ELIMINAR EN OTRAS FILAS:")
            for i in range(len(tabla)):
                if i != fila_pivote and abs(tabla[i][col_pivote]) > 1e-10:
                    factor = tabla[i][col_pivote]
                    self.pasos.append(f"   Fila {i+1}: Factor = {factor:.6f}")
                    self.pasos.append(f"   Nueva Fila {i+1} = Fila {i+1} - ({factor:.6f}) × Nueva Fila {fila_pivote+1}")
                    
                    for j in range(len(tabla[i])):
                        tabla[i][j] -= factor * tabla[fila_pivote][j]
                    self.pasos.append("")
            
            # Actualizar variable básica
            variables_basicas[fila_pivote] = var_entrante
            self.pasos.append(f"3️⃣ ACTUALIZAR BASE:")
            self.pasos.append(f"   {var_saliente} sale de la base")
            self.pasos.append(f"   {var_entrante} entra a la base")
            self.pasos.append("")
        
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
        if tipo_original == 'minimizar':
            valor_objetivo = -valor_objetivo
        valor_objetivo_mostrar = abs(valor_objetivo)
        
        self.pasos.append("")
        self.pasos.append("3. SOLUCIÓN ÓPTIMA - MÉTODO SIMPLEX ESTÁNDAR")
        self.pasos.append("")
        
        self.pasos.append("📋 VARIABLES DE DECISIÓN:")
        for i, (nombre, val) in enumerate(zip(nombres_variables, solucion)):
            self.pasos.append(f"   {nombre} = {val:.6f}")
        
        self.pasos.append("")
        self.pasos.append("📊 VARIABLES DE HOLGURA:")
        for i, var in enumerate(variables_basicas):
            if var not in nombres_variables and var.startswith('s'):
                self.pasos.append(f"   {var} = {tabla[i][-1]:.6f}")
        
        self.pasos.append("")
        self.pasos.append(f"🎯 VALOR ÓPTIMO: Z = {valor_objetivo_mostrar:.6f}")
        
        return {
            'solucion': solucion,
            'solucion_con_nombres': solucion_con_nombres,
            'nombres_variables': nombres_variables,
            'valor_objetivo': valor_objetivo_mostrar,
            'pasos': self.pasos,
            'tablas': self.tablas,
            'variables_basicas': variables_basicas,
            'tipo_optimizacion': tipo_original,
            'metodo_usado': 'Simplex Estándar'
        }
    
    def _mostrar_tabla_simplex_estandar(self, tabla, variables_basicas, nombres_variables, num_vars_originales):
        """Muestra la tabla Simplex estándar de manera formateada"""
        
        m = len(tabla) - 1  # número de restricciones
        n = len(tabla[0]) - 1  # número de variables
        
        self.pasos.append("📋 TABLA SIMPLEX:")
        self.pasos.append("")
        
        # Crear tabla HTML
        tabla_html = '<div class="simplex-table-container">'
        tabla_html += f'<div class="table-title">Iteración {self.iteracion}</div>'
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
        
        self.pasos.append(tabla_html)
        self.pasos.append("")
        
        return {
            'iteracion': self.iteracion,
            'tabla': [fila[:] for fila in tabla],
            'variables_basicas': variables_basicas[:],
            'tabla_html': tabla_html
        }


class MixedValue:
    """Clase para manejar valores de la forma a + bM donde M es la Gran M"""
    def __init__(self, coefficient=0, M_coefficient=0):
        self.coefficient = float(coefficient)
        self.M_coefficient = float(M_coefficient)
    
    def __add__(self, other):
        if isinstance(other, MixedValue):
            return MixedValue(
                self.coefficient + other.coefficient,
                self.M_coefficient + other.M_coefficient
            )
        else:
            return MixedValue(
                self.coefficient + float(other),
                self.M_coefficient
            )
    
    def __sub__(self, other):
        if isinstance(other, MixedValue):
            return MixedValue(
                self.coefficient - other.coefficient,
                self.M_coefficient - other.M_coefficient
            )
        else:
            return MixedValue(
                self.coefficient - float(other),
                self.M_coefficient
            )
    
    def __mul__(self, other):
        if isinstance(other, MixedValue):
            # (a + bM) * (c + dM) = ac + (ad + bc)M + bdM²
            # Como M es muy grande, M² se ignora en la práctica
            return MixedValue(
                self.coefficient * other.coefficient,
                self.coefficient * other.M_coefficient + self.M_coefficient * other.coefficient
            )
        else:
            other_val = float(other)
            return MixedValue(
                self.coefficient * other_val,
                self.M_coefficient * other_val
            )
    
    def __truediv__(self, other):
        if isinstance(other, MixedValue):
            if other.M_coefficient == 0:
                return MixedValue(
                    self.coefficient / other.coefficient,
                    self.M_coefficient / other.coefficient
                )
            else:
                raise ValueError("División por expresión con M no soportada")
        else:
            other_val = float(other)
            return MixedValue(
                self.coefficient / other_val,
                self.M_coefficient / other_val
            )
    
    def __neg__(self):
        return MixedValue(-self.coefficient, -self.M_coefficient)
    
    def is_negative(self):
        """Determina si el valor es negativo considerando M como muy grande"""
        if abs(self.M_coefficient) > 1e-10:
            return self.M_coefficient < 0
        else:
            return self.coefficient < -1e-10
    
    def is_zero(self):
        """Determina si el valor es cero"""
        return abs(self.coefficient) < 1e-10 and abs(self.M_coefficient) < 1e-10
    
    def to_display_string(self):
        """Convierte a string para mostrar"""
        if abs(self.coefficient) < 1e-10 and abs(self.M_coefficient) < 1e-10:
            return "0"
        elif abs(self.M_coefficient) < 1e-10:
            return f"{self.coefficient:.4f}"
        elif abs(self.coefficient) < 1e-10:
            if abs(self.M_coefficient - 1) < 1e-10:
                return "M"
            elif abs(self.M_coefficient + 1) < 1e-10:
                return "-M"
            else:
                return f"{self.M_coefficient:.4f}M"
        else:
            m_part = ""
            if abs(self.M_coefficient - 1) < 1e-10:
                m_part = "M"
            elif abs(self.M_coefficient + 1) < 1e-10:
                m_part = "-M"
            elif abs(self.M_coefficient) > 1e-10:
                m_part = f"{self.M_coefficient:.4f}M"
            
            if m_part:
                if self.M_coefficient > 0:
                    return f"{self.coefficient:.4f} + {m_part}"
                else:
                    return f"{self.coefficient:.4f} {m_part}"
            else:
                return f"{self.coefficient:.4f}"
    
    def __str__(self):
        return self.to_display_string()


class GranMSimplex:
    """Clase mejorada para resolver problemas de programación lineal usando el método de la Gran M"""
    
    def __init__(self):
        self.iteracion = 0
        self.pasos = []
        self.tablas = []
        self.M_value = 1000000  # Valor numérico de M para cálculos
        
    def resolver(self, funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables):
        """Resuelve un problema usando el método de la Gran M mejorado"""
        
        self.pasos = []
        self.tablas = []
        self.iteracion = 0
        
        # Preparar problema
        problema = self._preparar_problema_gran_m(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables)
        
        # Resolver
        return self._resolver_gran_m_mejorado(problema)
    
    def _preparar_problema_gran_m(self, c, restricciones, tipo, nombres_variables):
        """Prepara el problema para el método de la Gran M"""
        
        self.pasos.append("1. PREPARACIÓN DEL PROBLEMA - MÉTODO DE LA GRAN M MEJORADO")
        self.pasos.append("")
        self.pasos.append("📋 PROBLEMA ORIGINAL:")
        
        # Mostrar función objetivo
        if tipo == 'maximizar':
            self.pasos.append(f"   Maximizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
        else:
            self.pasos.append(f"   Minimizar: Z = " + " + ".join([f"{c[i]:.3f}·{nombres_variables[i]}" for i in range(len(c))]))
        
        self.pasos.append("   Sujeto a:")
        for i, rest in enumerate(restricciones):
            coef_str = " + ".join([f"{rest['coeficientes'][j]:.3f}·{nombres_variables[j]}" for j in range(len(rest['coeficientes']))])
            self.pasos.append(f"      {coef_str} {rest['tipo']} {rest['valor']:.3f}")
        
        self.pasos.append(f"      {', '.join(nombres_variables)} ≥ 0")
        self.pasos.append("")
        
        self.pasos.append("🔍 ANÁLISIS DE RESTRICCIONES:")
        necesita_artificial = []
        for i, rest in enumerate(restricciones):
            if rest['tipo'] == '>=':
                self.pasos.append(f"   Restricción {i+1}: Tipo ≥ → Requiere variable de exceso (-) y artificial (+)")
                necesita_artificial.append(i)
            elif rest['tipo'] == '=':
                self.pasos.append(f"   Restricción {i+1}: Tipo = → Requiere variable artificial (+)")
                necesita_artificial.append(i)
            else:
                self.pasos.append(f"   Restricción {i+1}: Tipo ≤ → Requiere variable de holgura (+)")
        
        self.pasos.append(f"   ➡️ Se aplicará el MÉTODO DE LA GRAN M")
        self.pasos.append("")
        
        # Configurar variables auxiliares
        num_vars_originales = len(c)
        variables_basicas = []
        variables_artificiales = []
        all_var_names = nombres_variables[:]
        
        # Contadores para variables auxiliares
        slack_count = 0
        surplus_count = 0
        artificial_count = 0
        
        # Crear matriz extendida con MixedValue
        A_extended = []
        b_extended = []
        
        for i, rest in enumerate(restricciones):
            fila = [MixedValue(coef, 0) for coef in rest['coeficientes']]
            b_val = MixedValue(rest['valor'], 0)
            
            if rest['tipo'] == '<=':
                # Variable de holgura
                slack_count += 1
                var_name = f"s{slack_count}"
                all_var_names.append(var_name)
                variables_basicas.append(var_name)
                
            elif rest['tipo'] == '>=':
                # Variable de exceso y artificial
                surplus_count += 1
                artificial_count += 1
                surplus_name = f"e{surplus_count}"
                artificial_name = f"a{artificial_count}"
                all_var_names.extend([surplus_name, artificial_name])
                variables_basicas.append(artificial_name)
                variables_artificiales.append(artificial_name)
                
            else:  # '='
                # Variable artificial
                artificial_count += 1
                artificial_name = f"a{artificial_count}"
                all_var_names.append(artificial_name)
                variables_basicas.append(artificial_name)
                variables_artificiales.append(artificial_name)
            
            A_extended.append(fila)
            b_extended.append(b_val)
        
        # Completar matriz A con variables auxiliares
        total_vars = len(all_var_names)
        
        # Expandir filas para incluir todas las variables
        for i, rest in enumerate(restricciones):
            while len(A_extended[i]) < total_vars:
                A_extended[i].append(MixedValue(0, 0))
        
        # Llenar columnas de variables auxiliares
        col_idx = num_vars_originales
        slack_idx = 0
        surplus_idx = 0
        artificial_idx = 0
        
        for i, rest in enumerate(restricciones):
            if rest['tipo'] == '<=':
                A_extended[i][col_idx] = MixedValue(1, 0)
                col_idx += 1
                
            elif rest['tipo'] == '>=':
                A_extended[i][col_idx] = MixedValue(-1, 0)  # Variable de exceso
                A_extended[i][col_idx + 1] = MixedValue(1, 0)  # Variable artificial
                col_idx += 2
                
            else:  # '='
                A_extended[i][col_idx] = MixedValue(1, 0)  # Variable artificial
                col_idx += 1
        
        # Crear función objetivo extendida
        c_extended = [MixedValue(coef, 0) for coef in c]
        
        # Agregar coeficientes para variables auxiliares
        for var_name in all_var_names[num_vars_originales:]:
            if var_name in variables_artificiales:
                # Variables artificiales tienen penalización M
                if tipo == 'maximizar':
                    c_extended.append(MixedValue(0, -1))  # -M para maximización
                else:
                    c_extended.append(MixedValue(0, 1))   # +M para minimización
            else:
                # Variables de holgura y exceso tienen coeficiente 0
                c_extended.append(MixedValue(0, 0))
        
        self.pasos.append("🔄 MODELO EXTENDIDO CON GRAN M:")
        self.pasos.append("")
        
        # Mostrar función objetivo extendida
        obj_parts = []
        for i, coef in enumerate(c_extended):
            var_name = all_var_names[i]
            if not coef.is_zero():
                coef_str = coef.to_display_string()
                if coef_str.startswith('-'):
                    obj_parts.append(f" {coef_str}·{var_name}")
                elif obj_parts:
                    obj_parts.append(f" + {coef_str}·{var_name}")
                else:
                    obj_parts.append(f"{coef_str}·{var_name}")
        
        obj_str = "Maximizar" if tipo == 'maximizar' else "Minimizar"
        obj_str += " Z = " + "".join(obj_parts)
        self.pasos.append(f"   {obj_str}")
        
        self.pasos.append("   Sujeto a:")
        for i, fila in enumerate(A_extended):
            constraint_parts = []
            for j, coef in enumerate(fila):
                if not coef.is_zero():
                    var_name = all_var_names[j]
                    coef_str = coef.to_display_string()
                    if coef_str.startswith('-'):
                        constraint_parts.append(f" {coef_str}·{var_name}")
                    elif constraint_parts:
                        constraint_parts.append(f" + {coef_str}·{var_name}")
                    else:
                        constraint_parts.append(f"{coef_str}·{var_name}")
            
            constraint_str = "".join(constraint_parts)
            rhs_str = b_extended[i].to_display_string()
            self.pasos.append(f"      {constraint_str} = {rhs_str}")
        
        self.pasos.append("")
        
        return {
            'A': A_extended,
            'b': b_extended,
            'c': c_extended,
            'variables_basicas': variables_basicas,
            'variables_artificiales': variables_artificiales,
            'all_var_names': all_var_names,
            'num_vars_originales': num_vars_originales,
            'tipo_original': tipo,
            'nombres_variables': nombres_variables
        }
    
    def _resolver_gran_m_mejorado(self, problema):
        """Resuelve usando el algoritmo de la Gran M mejorado"""
        
        A = problema['A']
        b = problema['b']
        c = problema['c']
        variables_basicas = problema['variables_basicas']
        variables_artificiales = problema['variables_artificiales']
        all_var_names = problema['all_var_names']
        num_vars_originales = problema['num_vars_originales']
        tipo_original = problema['tipo_original']
        nombres_variables = problema['nombres_variables']
        
        m = len(A)  # número de restricciones
        n = len(c)  # número de variables
        
        self.pasos.append("2. CONSTRUCCIÓN DE LA TABLA INICIAL")
        self.pasos.append("")
        
        # Crear tabla inicial con MixedValue
        tabla = []
        for i in range(m):
            fila = A[i][:] + [b[i]]
            tabla.append(fila)
        
        # Fila de la función objetivo
        if tipo_original == 'maximizar':
            fila_obj = [MixedValue(-coef.coefficient, -coef.M_coefficient) for coef in c] + [MixedValue(0, 0)]
        else:
            fila_obj = [MixedValue(coef.coefficient, coef.M_coefficient) for coef in c] + [MixedValue(0, 0)]
        tabla.append(fila_obj)
        
        # Eliminar variables artificiales de la función objetivo
        self.pasos.append("🔧 ELIMINACIÓN DE VARIABLES ARTIFICIALES DE LA FUNCIÓN OBJETIVO:")
        self.pasos.append("")
        
        for i, var_basica in enumerate(variables_basicas):
            if var_basica in variables_artificiales:
                # Encontrar la columna de esta variable artificial
                col_idx = all_var_names.index(var_basica)
                
                if not tabla[-1][col_idx].is_zero():
                    coef_obj = tabla[-1][col_idx]
                    self.pasos.append(f"   Eliminando {var_basica} (columna {col_idx + 1}):")
                    self.pasos.append(f"   Fila Z = Fila Z - ({coef_obj.to_display_string()}) × Fila {i + 1}")
                    
                    # Realizar la eliminación
                    for j in range(len(tabla[-1])):
                        tabla[-1][j] = tabla[-1][j] - coef_obj * tabla[i][j]
                    
                    self.pasos.append("")
        
        self.pasos.append("3. APLICACIÓN DEL ALGORITMO SIMPLEX")
        self.pasos.append("")
        
        self.iteracion = 0
        max_iterations = 50
        
        while self.iteracion < max_iterations:
            self.iteracion += 1
            self.pasos.append(f"ITERACIÓN {self.iteracion}")
            self.pasos.append("")
            
            # Mostrar tabla actual
            tabla_info = self._mostrar_tabla_gran_m_mejorada(tabla, variables_basicas, all_var_names)
            self.tablas.append(tabla_info)
            
            # Verificar optimalidad
            fila_obj_actual = tabla[-1][:-1]
            es_optimo = True
            for coef in fila_obj_actual:
                if coef.is_negative():
                    es_optimo = False
                    break
            
            if es_optimo:
                self.pasos.append("✓ CRITERIO DE OPTIMALIDAD CUMPLIDO")
                self.pasos.append("   Todos los coeficientes en la fila Z son ≥ 0")
                
                # Verificar factibilidad (variables artificiales deben ser cero)
                variables_artificiales_no_cero = []
                for i, var in enumerate(variables_basicas):
                    if var in variables_artificiales and not tabla[i][-1].is_zero():
                        variables_artificiales_no_cero.append((var, tabla[i][-1]))
                
                if variables_artificiales_no_cero:
                    self.pasos.append("")
                    self.pasos.append("❌ PROBLEMA SIN SOLUCIÓN FACTIBLE")
                    self.pasos.append("   Variables artificiales con valor no cero:")
                    for var, valor in variables_artificiales_no_cero:
                        self.pasos.append(f"      {var} = {valor.to_display_string()}")
                    
                    return {
                        'error': 'Problema sin solución factible - Las restricciones son inconsistentes',
                        'pasos': self.pasos,
                        'tablas': self.tablas,
                        'metodo_usado': 'Gran M Mejorado'
                    }
                
                self.pasos.append("✓ SOLUCIÓN FACTIBLE ENCONTRADA")
                self.pasos.append("¡SOLUCIÓN ÓPTIMA ALCANZADA!")
                break
            
            # Encontrar variable entrante (más negativa)
            col_pivote = -1
            valor_mas_negativo = None
            
            for j, coef in enumerate(fila_obj_actual):
                if coef.is_negative():
                    if valor_mas_negativo is None or self._es_mas_negativo(coef, valor_mas_negativo):
                        valor_mas_negativo = coef
                        col_pivote = j
            
            if col_pivote == -1:
                break
            
            var_entrante = all_var_names[col_pivote]
            self.pasos.append(f"🔵 VARIABLE ENTRANTE: {var_entrante} (columna {col_pivote + 1})")
            self.pasos.append(f"   Coeficiente: {valor_mas_negativo.to_display_string()}")
            self.pasos.append("")
            
            # Prueba de la razón mínima
            self.pasos.append("📊 PRUEBA DE RAZÓN MÍNIMA:")
            self.pasos.append("   Fila | Variable Base | b(i) | Coef. Columna | Razón")
            self.pasos.append("   " + "-" * 60)
            
            razones_validas = []
            
            for i in range(m):
                coef_col = tabla[i][col_pivote]
                rhs = tabla[i][-1]
                
                # Solo considerar coeficientes positivos sin componente M
                if coef_col.coefficient > 1e-10 and abs(coef_col.M_coefficient) < 1e-10:
                    if abs(rhs.M_coefficient) < 1e-10 and rhs.coefficient >= 0:
                        razon = rhs.coefficient / coef_col.coefficient
                        razones_validas.append((razon, i))
                        self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs.to_display_string():>8s} | {coef_col.to_display_string():>11s} | {razon:7.3f}")
                    else:
                        self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs.to_display_string():>8s} | {coef_col.to_display_string():>11s} | No válida")
                else:
                    self.pasos.append(f"   {i+1:2d}   | {variables_basicas[i]:11s} | {rhs.to_display_string():>8s} | {coef_col.to_display_string():>11s} | No válida")
            
            if not razones_validas:
                self.pasos.append("")
                self.pasos.append("❌ SOLUCIÓN NO ACOTADA")
                self.pasos.append("   No hay razones válidas para la prueba de razón mínima")
                return {
                    'error': 'Solución no acotada - La función objetivo puede crecer indefinidamente',
                    'pasos': self.pasos,
                    'tablas': self.tablas,
                    'metodo_usado': 'Gran M Mejorado'
                }
            
            # Encontrar razón mínima
            razon_min, fila_pivote = min(razones_validas)
            var_saliente = variables_basicas[fila_pivote]
            
            self.pasos.append("")
            self.pasos.append(f"🔴 VARIABLE SALIENTE: {var_saliente} (fila {fila_pivote + 1})")
            self.pasos.append(f"   Razón mínima: {razon_min:.6f}")
            self.pasos.append("")
            
            # Elemento pivote
            pivote = tabla[fila_pivote][col_pivote]
            self.pasos.append(f"⚡ ELEMENTO PIVOTE: {pivote.to_display_string()}")
            self.pasos.append(f"   Posición: Fila {fila_pivote + 1}, Columna {col_pivote + 1}")
            self.pasos.append("")
            
            # Actualizar información de pivote en la tabla
            if self.tablas:
                self.tablas[-1]['fila_pivote'] = fila_pivote
                self.tablas[-1]['col_pivote'] = col_pivote
                self.tablas[-1]['var_entrante'] = var_entrante
                self.tablas[-1]['var_saliente'] = var_saliente
                self.tablas[-1]['elemento_pivote'] = pivote.to_display_string()
            
            # Operaciones de pivoteo
            self.pasos.append("🔧 OPERACIONES DE PIVOTEO:")
            self.pasos.append("")
            
            # Normalizar fila pivote
            self.pasos.append(f"1️⃣ NORMALIZAR FILA PIVOTE (Fila {fila_pivote + 1}):")
            self.pasos.append(f"   Nueva Fila {fila_pivote + 1} = Fila {fila_pivote + 1} ÷ {pivote.to_display_string()}")
            
            for j in range(len(tabla[fila_pivote])):
                tabla[fila_pivote][j] = tabla[fila_pivote][j] / pivote
            
            self.pasos.append("")
            
            # Eliminar en otras filas
            self.pasos.append("2️⃣ ELIMINAR EN OTRAS FILAS:")
            for i in range(len(tabla)):
                if i != fila_pivote and not tabla[i][col_pivote].is_zero():
                    factor = tabla[i][col_pivote]
                    self.pasos.append(f"   Fila {i+1}: Factor = {factor.to_display_string()}")
                    self.pasos.append(f"   Nueva Fila {i+1} = Fila {i+1} - ({factor.to_display_string()}) × Nueva Fila {fila_pivote+1}")
                    
                    for j in range(len(tabla[i])):
                        tabla[i][j] = tabla[i][j] - factor * tabla[fila_pivote][j]
                    self.pasos.append("")
            
            # Actualizar variable básica
            variables_basicas[fila_pivote] = var_entrante
            self.pasos.append(f"3️⃣ ACTUALIZAR BASE:")
            self.pasos.append(f"   {var_saliente} sale de la base")
            self.pasos.append(f"   {var_entrante} entra a la base")
            self.pasos.append("")
        
        # Extraer solución final
        return self._extraer_solucion_final(tabla, variables_basicas, variables_artificiales, 
                                          all_var_names, num_vars_originales, nombres_variables, tipo_original)
    
    def _es_mas_negativo(self, val1, val2):
        """Compara si val1 es más negativo que val2 considerando M"""
        if abs(val1.M_coefficient - val2.M_coefficient) > 1e-10:
            return val1.M_coefficient < val2.M_coefficient
        else:
            return val1.coefficient < val2.coefficient
    
    def _mostrar_tabla_gran_m_mejorada(self, tabla, variables_basicas, all_var_names):
        """Muestra la tabla de la Gran M mejorada"""
        
        m = len(tabla) - 1  # número de restricciones
        n = len(tabla[0]) - 1  # número de variables
        
        self.pasos.append("📋 TABLA SIMPLEX (GRAN M):")
        self.pasos.append("")
        
        # Crear tabla HTML
        tabla_html = '<div class="simplex-table-container">'
        tabla_html += f'<div class="table-title">Iteración {self.iteracion} - Método Gran M</div>'
        tabla_html += '<table class="simplex-table table table-bordered table-hover">'
        
        # Encabezado
        tabla_html += '<thead class="table-dark"><tr>'
        tabla_html += '<th class="base-header text-center">Base</th>'
        for j in range(n):
            var_name = all_var_names[j]
            if var_name.startswith('a'):
                tabla_html += f'<th class="artificial-header text-center">{var_name}</th>'
            elif var_name.startswith('s'):
                tabla_html += f'<th class="slack-header text-center">{var_name}</th>'
            elif var_name.startswith('e'):
                tabla_html += f'<th class="surplus-header text-center">{var_name}</th>'
            else:
                tabla_html += f'<th class="var-header text-center">{var_name}</th>'
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
                tabla_html += f'<td class="{clase_celda}">{valor.to_display_string()}</td>'
            tabla_html += '</tr>'
        
        # Fila objetivo
        tabla_html += '<tr class="objective-row table-info">'
        tabla_html += '<td class="base-column objective-label text-center fw-bold">Z</td>'
        for j in range(len(tabla[-1])):
            valor = tabla[-1][j]
            clase_celda = f'objective-cell text-center data-col-{j}'
            if j == len(tabla[-1]) - 1:  # RHS column (valor de Z)
                clase_celda += ' objective-value fw-bold'
            tabla_html += f'<td class="{clase_celda}">{valor.to_display_string()}</td>'
        tabla_html += '</tr>'
        
        tabla_html += '</tbody></table>'
        tabla_html += '</div>'
        
        self.pasos.append(tabla_html)
        self.pasos.append("")
        
        return {
            'iteracion': self.iteracion,
            'tabla': [[valor.to_display_string() for valor in fila] for fila in tabla],
            'variables_basicas': variables_basicas[:],
            'tabla_html': tabla_html
        }
    
    def _extraer_solucion_final(self, tabla, variables_basicas, variables_artificiales, 
                               all_var_names, num_vars_originales, nombres_variables, tipo_original):
        """Extrae la solución final del problema"""
        
        # Extraer solución
        solucion = [0.0] * num_vars_originales
        solucion_con_nombres = {}
        
        for i, var in enumerate(variables_basicas):
            if var in nombres_variables:
                idx = nombres_variables.index(var)
                valor = tabla[i][-1]
                # Convertir MixedValue a float (debe ser solo coeficiente, sin M)
                if abs(valor.M_coefficient) < 1e-10:
                    solucion[idx] = valor.coefficient
                    solucion_con_nombres[var] = valor.coefficient
                else:
                    # Si hay componente M, el problema no es factible
                    return {
                        'error': 'Problema sin solución factible - Variables con componente M en la solución',
                        'pasos': self.pasos,
                        'tablas': self.tablas,
                        'metodo_usado': 'Gran M Mejorado'
                    }
        
        # Valor objetivo
        valor_z = tabla[-1][-1]
        if abs(valor_z.M_coefficient) > 1e-10:
            return {
                'error': 'Problema sin solución factible - Valor objetivo contiene M',
                'pasos': self.pasos,
                'tablas': self.tablas,
                'metodo_usado': 'Gran M Mejorado'
            }
        
        valor_objetivo = valor_z.coefficient
        if tipo_original == 'maximizar':
            valor_objetivo = -valor_objetivo
        
        self.pasos.append("")
        self.pasos.append("4. SOLUCIÓN ÓPTIMA - MÉTODO DE LA GRAN M")
        self.pasos.append("")
        
        self.pasos.append("🎯 SOLUCIÓN FINAL OBTENIDA:")
        self.pasos.append("")
        
        self.pasos.append("📋 VARIABLES DE DECISIÓN:")
        for i, (nombre, val) in enumerate(zip(nombres_variables, solucion)):
            self.pasos.append(f"   {nombre} = {val:.6f}")
        
        self.pasos.append("")
        self.pasos.append("📊 VARIABLES AUXILIARES:")
        for i, var in enumerate(variables_basicas):
            if var not in nombres_variables:
                valor = tabla[i][-1]
                if var in variables_artificiales:
                    self.pasos.append(f"   {var} = {valor.to_display_string()} (artificial - debe ser 0)")
                else:
                    self.pasos.append(f"   {var} = {valor.to_display_string()}")
        
        self.pasos.append("")
        self.pasos.append(f"🎯 VALOR ÓPTIMO: Z = {abs(valor_objetivo):.6f}")
        
        return {
            'solucion': solucion,
            'solucion_con_nombres': solucion_con_nombres,
            'nombres_variables': nombres_variables,
            'valor_objetivo': abs(valor_objetivo),
            'pasos': self.pasos,
            'tablas': self.tablas,
            'variables_basicas': variables_basicas,
            'tipo_optimizacion': tipo_original,
            'metodo_usado': 'Gran M Mejorado'
        }

# ==================== FUNCIÓN PRINCIPAL PARA RESOLVER SIMPLEX ====================

def preparar_problema_simplex(c, restricciones, tipo, nombres_variables, pasos):
    """Detecta qué método usar y prepara el problema"""
    
    # Detectar si necesitamos el método de la Gran M
    necesita_gran_m = any(rest['tipo'] in ['>=', '='] for rest in restricciones)
    
    if necesita_gran_m:
        # Usar método de la Gran MF
        solver = GranMSimplex()
        return solver.resolver(c, restricciones, tipo, nombres_variables)
    else:
        # Usar método Simplex estándar
        solver = SimplexEstandar()
        return solver.resolver(c, restricciones, tipo, nombres_variables)

def metodo_simplex(problema, pasos):
    """Función de compatibilidad - redirige al método apropiado"""
    # Esta función se mantiene para compatibilidad con el código existente
    # pero ahora redirige a la función principal
    return preparar_problema_simplex(
        problema['c'], 
        [{'coeficientes': problema['A'][i], 'tipo': '<=', 'valor': problema['b'][i]} for i in range(len(problema['A']))],
        problema['tipo_original'],
        problema['nombres_variables'],
        pasos
    )
