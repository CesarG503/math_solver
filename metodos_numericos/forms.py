from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuarios, Ejercicio

class FormCrearUsuario(UserCreationForm):
    image = forms.ImageField(required=True, label='Imagen de perfil')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'image')

    def save(self, commit=True):
        user = super().save(commit=commit)
        image = self.cleaned_data.get('image')
        if image:
            user.usuarios.image = image
            if(commit):
                user.save()
        return user
    
class FormEditarUsuario(UserChangeForm):
    image = forms.ImageField(required=False, label='Imagen de perfil')

    class Meta:
        model = User
        fields = ('username', 'email', 'image')

    def save(self, commit=True):
        user = super().save(commit=commit)
        image = self.cleaned_data.get('image')
        if image:
            user.usuarios.image = image
            if(commit):
                user.save()
        return user

class FormGuardarHistorial(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['tipo', 'ecuacion', 'puntos', 'solucion','user']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        ejercicio = super().save(commit=commit)
        if self.user:
            ejercicio.user = self.user
        if commit:
            ejercicio.save()
        return ejercicio