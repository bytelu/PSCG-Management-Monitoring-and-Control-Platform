# Generated by Django 5.0.4 on 2024-07-05 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OICSec', '0012_tipocedula_cedula_id_archivo_cedula_id_tipo_cedula'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cedula',
            name='id_tipo_cedula',
        ),
    ]