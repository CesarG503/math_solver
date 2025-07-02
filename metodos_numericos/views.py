from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import FormCrearUsuario
from .models import Ejercicio
from .utils import interpolacion_hermite, integracion_compuesta, metodo_simplex
import json

def index(request):
    """Vista principal con opciones de métodos numéricos"""
    return render(request, 'metodos_numericos/index.html')

def hermite_view(request, id_ejercicio=None):
    """Vista para interpolación de Hermite"""
    context = {}

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            puntos_data = request.POST.get('puntos', '')
            x_eval = float(request.POST.get('x_eval', 0))

            # Parsear puntos (formato: x1,f1,df1;x2,f2,df2;...)
            puntos = []
            if puntos_data.strip():
                for punto_str in puntos_data.strip().split(';'):
                    if punto_str.strip():
                        try:
                            x, f, df = map(float, punto_str.split(','))
                            puntos.append((x, f, df))
                        except ValueError:
                            messages.error(request, f'Formato inválido en punto: {punto_str}')
                            return render(request, 'metodos_numericos/hermite.html', context)

            if len(puntos) < 2:
                messages.error(request, 'Se necesitan al menos 2 puntos para la interpolación.')
                return render(request, 'metodos_numericos/hermite.html', context)

            # Validar que no hay x duplicados
            x_values = [p[0] for p in puntos]
            if len(set(x_values)) != len(x_values):
                messages.error(request, 'Los valores de x deben ser únicos.')
                return render(request, 'metodos_numericos/hermite.html', context)
            
            # Calcular interpolación de Hermite
            resultado = interpolacion_hermite(puntos, x_eval)
            
            # Generar datos para gráfica
            from .utils import generar_datos_grafica_hermite
            datos_grafica = generar_datos_grafica_hermite(puntos, resultado['polinomio'], x_eval)
            if datos_grafica:
                context['datos_grafica'] = json.dumps(datos_grafica)

            # Mantener los datos de entrada para repoblar el formulario
            context['mantener_puntos'] = True
            context.update(resultado)
            context['puntos_input'] = puntos_data
            context['x_eval'] = x_eval
            
            guardar_ejercicio(request.user.id, 'hermite', "|".join([puntos_data, str(x_eval)]), resultado['polinomio_latex'])
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')

        return render(request, 'metodos_numericos/hermite.html', context)
    
    # Si se proporciona un id_ejercicio, intentar cargar el ejercicio existente
    if id_ejercicio:
        try:
            # Cargar ejercicio existente
            from .models import Ejercicio
            ejercicio = Ejercicio.objects.get(id=id_ejercicio, user=request.user)
            context['ejercicio_db'] = ejercicio
            
            # Mantener los datos del ejercicio en el formulario
            x_eval_input = ejercicio.puntos.split("|")[1]
            puntos_input = ejercicio.puntos.split("|")[0].split(";")
            puntos_input_db = ""
            for punto in puntos_input:
                punto_s = punto.split(',')
                puntos_input_db += f"{punto_s[0]},{punto_s[1]},{punto_s[2]};"

            context['puntos_input_db'] = puntos_input_db
            context['x_eval'] = x_eval_input
        except Ejercicio.DoesNotExist:
            messages.error(request, 'Ejercicio no encontrado o no autorizado.')
            return redirect('metodos_numericos:hermite')

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('metodos_numericos:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('metodos_numericos:index')
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'auth/login.html', {'form': form})
        else:
            return render(request, 'auth/login.html', {'form': form,'error':'Credenciales Incorrectas'})
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def sing_up_view(request):
    if request.user.is_authenticated:
        return redirect('metodos_numericos:index')
    
    if( request.method == 'POST'):
        form = FormCrearUsuario(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            return redirect('metodos_numericos:index')
        else:
            return render(request, 'auth/register.html', {'form': form})
    else:
        form = FormCrearUsuario()
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('metodos_numericos:index')

def simplex_view(request):
    """Vista para el método Simplex"""
    context = {}
    
    if request.method == 'POST':
        try:
            # Obtener función objetivo desde el campo oculto procesado por JavaScript
            funcion_objetivo_str = request.POST.get('funcion_objetivo', '')
            tipo_optimizacion = request.POST.get('tipo_optimizacion', 'maximizar')
            nombres_variables_str = request.POST.get('nombres_variables', '')
            
            # Debug: imprimir los datos recibidos
            print(f"Función objetivo recibida: '{funcion_objetivo_str}'")
            print(f"Nombres variables: '{nombres_variables_str}'")
            
            # Parsear función objetivo
            funcion_objetivo = []
            if funcion_objetivo_str.strip():
                for coef_str in funcion_objetivo_str.split(','):
                    if coef_str.strip():
                        try:
                            funcion_objetivo.append(float(coef_str.strip()))
                        except ValueError:
                            messages.error(request, f'Coeficiente inválido en función objetivo: {coef_str}')
                            return render(request, 'metodos_numericos/simplex.html', context)
            
            # Parsear nombres de variables
            nombres_variables = []
            if nombres_variables_str.strip():
                for nombre in nombres_variables_str.split(','):
                    if nombre.strip():
                        nombres_variables.append(nombre.strip())
            
            # Si no hay nombres personalizados, usar por defecto
            if not nombres_variables:
                nombres_variables = [f'x{i+1}' for i in range(len(funcion_objetivo))]
            
            if not funcion_objetivo:
                messages.error(request, 'Debe ingresar al menos un coeficiente en la función objetivo.')
                return render(request, 'metodos_numericos/simplex.html', context)
            
            # Obtener restricciones procesadas por JavaScript
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
                
                print(f"Restricción {i}: coef='{coef_str}', tipo='{tipo_rest}', valor='{valor_str}'")
                
                if coef_str.strip():
                    coeficientes = []
                    for coef in coef_str.split(','):
                        if coef.strip():
                            try:
                                coeficientes.append(float(coef.strip()))
                            except ValueError:
                                messages.error(request, f'Coeficiente inválido en restricción {i+1}: {coef}')
                                return render(request, 'metodos_numericos/simplex.html', context)
                    
                    # Ajustar longitud de coeficientes a la función objetivo
                    while len(coeficientes) < len(funcion_objetivo):
                        coeficientes.append(0)
                    coeficientes = coeficientes[:len(funcion_objetivo)]
                    
                    try:
                        valor = float(valor_str)
                        restricciones.append({
                            'coeficientes': coeficientes,
                            'tipo': tipo_rest,
                            'valor': valor
                        })
                    except ValueError:
                        messages.error(request, f'Valor inválido en restricción {i+1}: {valor_str}')
                        return render(request, 'metodos_numericos/simplex.html', context)
                
                i += 1
            
            if not restricciones:
                messages.error(request, 'Debe ingresar al menos una restricción.')
                return render(request, 'metodos_numericos/simplex.html', context)
            
            print(f"Función objetivo final: {funcion_objetivo}")
            print(f"Restricciones finales: {restricciones}")
            
            # Resolver usando Simplex
            resultado = resolver_simplex(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables)
            
            # Generar datos para gráfica (solo para 2 variables)
            if len(funcion_objetivo) == 2:
                from .utils import generar_datos_grafica_simplex
                solucion_para_grafica = resultado.get('solucion', None)
                datos_grafica = generar_datos_grafica_simplex(
                    funcion_objetivo, restricciones, solucion_para_grafica, 
                    nombres_variables, tipo_optimizacion
                )
                if datos_grafica:
                    context['datos_grafica'] = json.dumps(datos_grafica)

            context.update(resultado)
            # Mantener los datos de entrada para repoblar el formulario
            context['mantener_datos'] = True
            context.update({
                'funcion_objetivo_input': funcion_objetivo_str,
                'tipo_optimizacion': tipo_optimizacion,
                'num_restricciones': len(restricciones),
                'restricciones_data': restricciones,
                'nombres_variables': nombres_variables,
                'num_variables': len(funcion_objetivo),
                'funcion_objetivo_valores': funcion_objetivo,  # Valores numéricos para repoblar
                'nombres_variables_str': nombres_variables_str  # String original
            })
            
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')
            print(f"Error completo: {e}")
            import traceback
            traceback.print_exc()
    
    return render(request, 'metodos_numericos/simplex.html', context)

def resolver_simplex(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables):
    """Función auxiliar para resolver el problema Simplex usando la nueva estructura orientada a objetos"""
    from .utils import SimplexEstandar, GranMSimplex
    pasos = []
    # Detectar si se requiere Gran M
    necesita_gran_m = any(r['tipo'] in ['>=', '='] for r in restricciones)
    if necesita_gran_m:
        solver = GranMSimplex()
        resultado = solver.resolver(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables)
        resultado['metodo_usado'] = 'Gran M'
    else:
        solver = SimplexEstandar()
        resultado = solver.resolver(funcion_objetivo, restricciones, tipo_optimizacion, nombres_variables)
        resultado['metodo_usado'] = 'Simplex Estándar'
    return resultado

def guardar_ejercicio(uid, tipo, puntos, polinomio_solucion):
    if( uid and tipo and puntos and polinomio_solucion):
        if Ejercicio.objects.filter(user_id=uid, tipo=tipo, puntos=puntos).exists():
            # Si ya existe un ejercicio con esos parámetros, no lo guardamos de nuevo
            return False
        ejercicio = Ejercicio(user_id=uid, tipo=tipo, puntos=puntos, solucion=polinomio_solucion)
        ejercicio.save()
        return True