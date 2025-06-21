from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuarios

class UsersAdmin(UserAdmin):
    model = Usuarios
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

admin.site.register(Usuarios, UsersAdmin)