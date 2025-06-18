from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuarios(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    class Meta:
        db_table = 'tbl_usuarios'
