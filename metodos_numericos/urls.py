from django.urls import path
from . import views, api

app_name = 'metodos_numericos'

urlpatterns = [
    path('', views.docs, name='docs'),
    path('index/', views.index, name='index'),
    path('docs/', views.docs, name='docs_alt'),
    path('hermite/', views.hermite_view, name='hermite'),
    path('hermite/<int:id_ejercicio>/', views.hermite_view, name='hermite_id'),
    path('integracion/', views.integracion_view, name='integracion'),
    path('simplex/', views.simplex_view, name='simplex'),
    path('simplex/<int:id_ejercicio>/', views.simplex_view, name='simplex_id'),
    path('simplex/clone/<int:id_ejercicio>/', views.simplex_view, name='simplex_id'),
    path('history/', views.history_view, name='history'),
    #Authentication URLs
    path('login/', views.login_view, name='login'),
    path('change/', api.editar_usuario, name='change'),
    path('signup/', views.sing_up_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    #Ejercicios URLs
    path('ejercicios/', api.ejercicios, name='ejercicios'),
    path('eliminar-hermite/<int:id_ejercicio>/', api.eliminar_hermite, name='eliminar_hermite'),
    path('eliminar-simplex/<int:id_ejercicio>/', api.eliminar_simplex, name='eliminar_simplex'),
]
