# Generated by Django 3.0.2 on 2020-03-12 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_auto_20200306_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='set',
            name='difficulty',
            field=models.CharField(blank=True, choices=[('E', 'Easy'), ('M', 'In the middle'), ('H', 'Hard')], default='Easy', max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='distance_unit',
            field=models.CharField(blank=True, choices=[('mi', 'mi'), ('km', 'km')], default='mi', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='notes',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='reps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='time_unit',
            field=models.CharField(blank=True, choices=[('sec', 'sec'), ('min', 'min')], default='sec', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='unit',
            field=models.CharField(blank=True, choices=[('lbs', 'lbs'), ('kg', 'kg')], default='lbs', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
