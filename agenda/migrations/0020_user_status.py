# Generated by Django 5.0.3 on 2024-04-23 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0019_empresa_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="status",
            field=models.BooleanField(default=True),
        ),
    ]
