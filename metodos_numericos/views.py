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
            if(request.user.is_authenticated):
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

def integracion_view(request, id_ejercicio=None):
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
            if(request.user.is_authenticated):
                guardar_integracion(request.user.id, 'integracion', f"{funcion}!{a},{b},{n}!{metodo}", resultado['resultado'])
        except ValueError as e:
            messages.error(request, f'Error en los datos de entrada: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')
        return render(request, 'metodos_numericos/integracion.html', context)
    
    if id_ejercicio:
        try:
            # Cargar ejercicio existente
            from .models import Ejercicio
            ejercicio = Ejercicio.objects.get(id=id_ejercicio, user=request.user)
            context['ejercicio_db'] = ejercicio.ecuacion
            
            # Mantener los datos del ejercicio en el formulario
            funcion_input = ejercicio.ecuacion.split("!")[0]
            a_input, b_input, n_input = map(float, ejercicio.ecuacion.split("!")[1].split(","))
            metodo_input = ejercicio.ecuacion.split("!")[2]
            
            context['funcion_input_db'] = funcion_input
            context['a'] = a_input
            context['b'] = b_input
            context['n'] = n_input
            context['metodo'] = metodo_input
            
        except Ejercicio.DoesNotExist:
            messages.error(request, 'Ejercicio no encontrado o no autorizado.')
            return redirect('metodos_numericos:integracion')

    return render(request, 'metodos_numericos/integracion.html', context)

@login_required
def history_view(request):
    """Vista para mostrar el historial de ejercicios del usuario"""
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para ver tu historial.')
        return redirect('metodos_numericos:login')
    
    ejercicios = Ejercicio.objects.filter(user=request.user).order_by('-fecha_creacion')
    
    context = {
        'ejercicios': ejercicios
    }
    
    return render(request, 'metodos_numericos/history.html', context)  

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

def guardar_ejercicio(uid, tipo, puntos, polinomio_solucion):
    if( uid and tipo and puntos and polinomio_solucion):
        if Ejercicio.objects.filter(user_id=uid, tipo=tipo, puntos=puntos).exists():
            # Si ya existe un ejercicio con esos parámetros, no lo guardamos de nuevo
            return False
        ejercicio = Ejercicio(user_id=uid, tipo=tipo, puntos=puntos, solucion=polinomio_solucion)
        ejercicio.save()
        return True
    
def guardar_integracion(uid, tipo, ecuacion, polinomio_solucion):
    if(uid and tipo and ecuacion and polinomio_solucion):
        if Ejercicio.objects.filter(user_id=uid, tipo=tipo, ecuacion=ecuacion).exists():
            return False
        ejercicio = Ejercicio(user_id=uid, tipo=tipo, ecuacion=ecuacion, solucion=polinomio_solucion)
        ejercicio.save()
        return True