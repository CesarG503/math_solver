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
