from django.urls import path
from . import views

app_name = 'metodos_numericos'

urlpatterns = [
    path('', views.index, name='index'),
    path('hermite/', views.hermite_view, name='hermite'),
    path('integracion/', views.integracion_view, name='integracion'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.sing_up_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('simplex/', views.simplex_view, name='simplex'),
]
