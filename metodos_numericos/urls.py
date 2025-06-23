from django.urls import path
from . import views, api

app_name = 'metodos_numericos'

urlpatterns = [
    path('', views.index, name='index'),
    path('hermite/', views.hermite_view, name='hermite'),
    path('integracion/', views.integracion_view, name='integracion'),
    path('simplex/', views.simplex_view, name='simplex'),
    #Authentication URLs
    path('login/', views.login_view, name='login'),
    path('change/', api.editar_usuario, name='change'),
    path('signup/', views.sing_up_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
