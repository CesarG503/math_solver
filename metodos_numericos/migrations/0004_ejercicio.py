# Generated by Django 5.2.3 on 2025-06-23 17:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metodos_numericos", "0003_delete_ejercicio"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ejercicio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tipo", models.CharField(max_length=100)),
                ("ecuacion", models.TextField()),
                ("puntos", models.TextField()),
                ("solucion", models.TextField()),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "tbl_ejercicios",
            },
        ),
    ]
