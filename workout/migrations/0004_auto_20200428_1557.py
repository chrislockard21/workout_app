# Generated by Django 3.0.2 on 2020-04-28 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0003_auto_20200327_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercisebygroup',
            name='type',
            field=models.CharField(choices=[('CHEST', 'CHEST'), ('BACK', 'BACK'), ('ARMS', 'ARMS'), ('LEGS', 'LEGS'), ('ABS', 'ABS'), ('SHOULDERS', 'SHOULDERS')], max_length=15),
        ),
    ]
