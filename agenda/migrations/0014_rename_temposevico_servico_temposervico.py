# Generated by Django 5.0.3 on 2024-04-07 01:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0013_rename_horaincial_diasemanafuncionario_horainicial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="servico",
            old_name="tempoSevico",
            new_name="tempoServico",
        ),
    ]