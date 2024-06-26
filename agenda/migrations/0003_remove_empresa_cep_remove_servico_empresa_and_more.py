# Generated by Django 5.0.3 on 2024-03-27 17:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0002_alter_user_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="empresa",
            name="cep",
        ),
        migrations.RemoveField(
            model_name="servico",
            name="empresa",
        ),
        migrations.CreateModel(
            name="EmpresaServico",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("cep", models.CharField(blank=True, max_length=200, null=True)),
                ("numero", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "complemento",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="agenda.empresa",
                    ),
                ),
                (
                    "servico",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="agenda.servico",
                    ),
                ),
            ],
        ),
    ]
