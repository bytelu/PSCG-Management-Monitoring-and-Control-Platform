# Generated by Django 5.0.4 on 2024-06-25 17:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OICSec', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorRevision',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('clave', models.IntegerField(blank=True, null=True)),
                ('tipo', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'sector_revision',
            },
        ),
        migrations.AddField(
            model_name='controlinterno',
            name='id_sector_revision',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='OICSec.sectorrevision'),
        ),
    ]
