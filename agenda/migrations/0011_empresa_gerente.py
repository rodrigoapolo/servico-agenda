# Generated by Django 5.0.3 on 2024-04-04 16:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0010_empresa_cep_empresa_complemento_empresa_numero_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="empresa",
            name="gerente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]