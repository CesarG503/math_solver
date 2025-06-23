from django.shortcuts import render
from django.contrib import messages
from .utils import interpolacion_hermite, integracion_compuesta, metodo_simplex
import json

def index(request):
    """Vista principal con opciones de métodos numéricos"""
    return render(request, 'metodos_numericos/index.html')

def hermite_view(request):
    """Vista para interpolación de Hermite"""
    context = {}
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            puntos_data = request.POST.get('puntos', '')
            x_eval = float(request.POST.get('x_eval', 0))
            
            # Parsear puntos (formato: x1,f1,df1;x2,f2,df2;...)
            puntos = []
            for punto_str in puntos_data.strip().split(';'):
                if punto_str.strip():
                    x, f, df = map(float, punto_str.split(','))
                    puntos.append((x, f, df))
            
            if len(puntos) < 2:
                messages.error(request, 'Se necesitan al menos 2 puntos para la interpolación.')
                return render(request, 'metodos_numericos/hermite.html', context)
            
            # Calcular interpolación de Hermite
            resultado = interpolacion_hermite(puntos, x_eval)
            
            # Generar datos para gráfica
            from .utils import generar_datos_grafica_hermite
            datos_grafica = generar_datos_grafica_hermite(puntos, resultado['polinomio'], x_eval)
            if datos_grafica:
                context['datos_grafica'] = json.dumps(datos_grafica)

            context.update(resultado)
            context['puntos_input'] = puntos_data
            context['x_eval'] = x_eval
            
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')
    
    return render(request, 'metodos_numericos/hermite.html', context)

def integracion_view(request):
    """Vista para integración numérica compuesta"""
    context = {}
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            # Usar el campo oculto que contiene la expresión convertida
            funcion = request.POST.get('funcion', '')
            if not funcion:
                # Fallback al campo visible si el oculto está vacío
                funcion = request.POST.get('funcion', '')
            
            a = float(request.POST.get('a', 0))
            b = float(request.POST.get('b', 1))
            n = int(request.POST.get('n', 4))
            metodo = request.POST.get('metodo', 'trapecio')
            
            if n <= 0:
                messages.error(request, 'El número de subintervalos debe ser positivo.')
                return render(request, 'metodos_numericos/integracion.html', context)
            
            if a >= b:
                messages.error(request, 'El límite inferior debe ser menor que el superior.')
                return render(request, 'metodos_numericos/integracion.html', context)
            
            # Calcular integración
            resultado = integracion_compuesta(funcion, a, b, n, metodo)

            # Generar datos para gráfica
            from .utils import generar_datos_grafica_integracion
            datos_grafica = generar_datos_grafica_integracion(funcion, a, b, n, metodo, resultado['resultado'])
            if datos_grafica:
                context['datos_grafica'] = json.dumps(datos_grafica)

            h = (b - a) / n  # Calcular el ancho de subintervalo
            context.update(resultado)
            context.update({
                'funcion_input': funcion,
                'a': a,
                'b': b,
                'n': n,
                'metodo': metodo,
                'h': h  
            })
            
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')
    
    return render(request, 'metodos_numericos/integracion.html', context)

def simplex_view(request):
    """Vista para el método Simplex"""
    context = {}
    
    if request.method == 'POST':
        try:
            # Obtener función objetivo
            funcion_objetivo_str = request.POST.get('funcion_objetivo', '')
            tipo_optimizacion = request.POST.get('tipo_optimizacion', 'maximizar')
            
            # Parsear función objetivo
            funcion_objetivo = []
            for coef_str in funcion_objetivo_str.split(','):
                if coef_str.strip():
                    funcion_objetivo.append(float(coef_str.strip()))
            
            if not funcion_objetivo:
                messages.error(request, 'Debe ingresar al menos un coeficiente en la función objetivo.')
                return render(request, 'metodos_numericos/simplex.html', context)
            
            # Obtener restricciones
            restricciones = []
            i = 0
            while True:
                coef_key = f'restriccion_{i}_coeficientes'
                tipo_key = f'restriccion_{i}_tipo'
                valor_key = f'restriccion_{i}_valor'
                
                if coef_key not in request.POST:
                    break
                
                coef_str = request.POST.get(coef_key, '')
                tipo_rest = request.POST.get(tipo_key, '<=')
                valor_str = request.POST.get(valor_key, '0')
                
                if coef_str.strip():
                    coeficientes = []
                    for coef in coef_str.split(','):
                        if coef.strip():
                            coeficientes.append(float(coef.strip()))
                    
                    # Ajustar longitud de coeficientes a la función objetivo
                    while len(coeficientes) < len(funcion_objetivo):
                        coeficientes.append(0)
                    coeficientes = coeficientes[:len(funcion_objetivo)]
                    
                    restricciones.append({
                        'coeficientes': coeficientes,
                        'tipo': tipo_rest,
                        'valor': float(valor_str)
                    })
                
                i += 1
            
            if not restricciones:
                messages.error(request, 'Debe ingresar al menos una restricción.')
                return render(request, 'metodos_numericos/simplex.html', context)
            
            # Resolver usando Simplex
            resultado = metodo_simplex(funcion_objetivo, restricciones, tipo_optimizacion)
            
            context.update(resultado)
            context.update({
                'funcion_objetivo_input': funcion_objetivo_str,
                'tipo_optimizacion': tipo_optimizacion,
                'num_restricciones': len(restricciones),
                'restricciones_data': restricciones
            })
            
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')
    
    return render(request, 'metodos_numericos/simplex.html', context)