from django.urls import path
from . import views

app_name = 'metodos_numericos'

urlpatterns = [
    path('', views.index, name='index'),
    path('hermite/', views.hermite_view, name='hermite'),
    path('integracion/', views.integracion_view, name='integracion'),
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
]
