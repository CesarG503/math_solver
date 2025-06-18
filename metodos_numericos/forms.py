from django import forms
from .models import Usuarios

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ('username', 'email', 'profile_picture', 'password')
