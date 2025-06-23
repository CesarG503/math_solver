from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FormEditarUsuario

@login_required
def editar_usuario(request):
    if request.method == 'GET':
        return redirect('metodos_numericos:index')

    if request.method == 'POST':
        form = FormEditarUsuario(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('metodos_numericos:index')
        else:
            messages.error(request, 'Error al actualizar el perfil. Por favor, corrige los errores.')
    else:
        messages.error(request,"No se ha enviado ningún dato para actualizar el perfil.")
        return redirect(request, 'metodos_numericos:index')