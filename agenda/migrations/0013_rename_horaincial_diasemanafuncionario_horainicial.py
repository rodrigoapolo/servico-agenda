# Generated by Django 5.0.3 on 2024-04-07 01:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0012_agenda_funcionario_alter_agenda_cliente"),
    ]

    operations = [
        migrations.RenameField(
            model_name="diasemanafuncionario",
            old_name="horaIncial",
            new_name="horaInicial",
        ),
    ]