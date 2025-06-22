from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuarios

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