# Generated by Django 2.0.6 on 2020-03-31 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0007_auto_20200327_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='set',
            name='distance',
        ),
        migrations.RemoveField(
            model_name='set',
            name='distance_unit',
        ),
        migrations.RemoveField(
            model_name='set',
            name='time',
        ),
        migrations.RemoveField(
            model_name='set',
            name='time_unit',
        ),
        migrations.RemoveField(
            model_name='sethistory',
            name='distance',
        ),
        migrations.RemoveField(
            model_name='sethistory',
            name='distance_unit',
        ),
        migrations.RemoveField(
            model_name='sethistory',
            name='time',
        ),
        migrations.RemoveField(
            model_name='sethistory',
            name='time_unit',
        ),
    ]
