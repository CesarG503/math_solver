from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models

class Ejercicio(models.Model):
    tipo = models.CharField(max_length=100)
    ecuacion = models.TextField()
    puntos = models.TextField()
    restricciones = models.JSONField()
    solucion = models.TextField()
    user = user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField()

    def __str__(self):
        return f"{self.tipo} - {self.ecuacion}"
    
    class Meta:
        db_table = 'tbl_ejercicios'

class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image  = models.ImageField(upload_to='perfiles/', default='perfiles/default.png')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'tbl_usuarios'

@receiver(post_save, sender=User)
def crear_o_editar_perfil(sender, instance, created, **kwargs):
    if created:
        Usuarios.objects.create(user=instance)
    instance.usuarios.save()