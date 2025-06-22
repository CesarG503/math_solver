from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import FormCrearUsuario
from .utils import interpolacion_hermite, integracion_compuesta

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
            return render(request, 'auth/login.html', {'form': form})
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