from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuarios(AbstractUser):

    class Meta:
        db_table = 'tbl_usuarios'
