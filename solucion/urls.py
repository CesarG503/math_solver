"""
URL configuration for solucion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import template
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('metodos_numericos.urls')),
        # Recuperacion de contraseña
    path('reset_password/',
          auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"),
          name='password_reset'),
    path('reset_password_sent/',
          auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"),
          name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"),
          name='password_reset_confirm'),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"),
        name='password_reset_complete'),
    #Language switcher URLs
    path('i18n/', include('django.conf.urls.i18n')),
        #Cambio de contraseña
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(template_name='auth/change_password.html'), 
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='auth/change_done.html'), name='password_change_done'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


