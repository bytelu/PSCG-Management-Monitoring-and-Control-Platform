# Generated by Django 5.0.4 on 2024-07-09 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OICSec', '0018_alter_archivo_archivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivo',
            name='nombre',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
    ]
