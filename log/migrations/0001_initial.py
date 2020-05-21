# Generated by Django 3.0.2 on 2020-03-03 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(null=True)),
                ('status', models.CharField(max_length=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.Workout')),
            ],
        ),
        migrations.CreateModel(
            name='LiftingSetHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('CHEST', 'CHEST'), ('BACK', 'BACK'), ('ARMS', 'ARMS'), ('LEGS', 'LEGS'), ('ABS', 'ABS'), ('CARDIO', 'CARDIO')], max_length=15)),
                ('reps', models.FloatField()),
                ('weight', models.FloatField()),
                ('unit', models.CharField(choices=[('lbs', 'lbs'), ('kg', 'kg')], default='lbs', max_length=3)),
                ('difficulty', models.CharField(choices=[('E', 'Easy'), ('M', 'In the middle'), ('H', 'Hard')], default='Easy', max_length=1)),
                ('notes', models.CharField(blank=True, max_length=50)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.ExerciseByGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LiftingSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reps', models.IntegerField()),
                ('weight', models.FloatField()),
                ('unit', models.CharField(choices=[('lbs', 'lbs'), ('kg', 'kg')], default='lbs', max_length=3)),
                ('difficulty', models.CharField(choices=[('E', 'Easy'), ('M', 'In the middle'), ('H', 'Hard')], default='Easy', max_length=1)),
                ('notes', models.CharField(blank=True, max_length=50)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.Exercise')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='log.Log')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardioSetHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('CHEST', 'CHEST'), ('BACK', 'BACK'), ('ARMS', 'ARMS'), ('LEGS', 'LEGS'), ('ABS', 'ABS'), ('CARDIO', 'CARDIO')], max_length=15)),
                ('distance', models.FloatField()),
                ('distance_unit', models.CharField(choices=[('mi', 'mi'), ('km', 'km')], default='mi', max_length=2)),
                ('time', models.FloatField()),
                ('time_unit', models.CharField(choices=[('sec', 'sec'), ('min', 'min')], default='sec', max_length=3)),
                ('notes', models.CharField(blank=True, max_length=50)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.ExerciseByGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardioSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('distance', models.IntegerField()),
                ('distance_unit', models.CharField(choices=[('mi', 'mi'), ('km', 'km')], default='mi', max_length=2)),
                ('time', models.FloatField()),
                ('time_unit', models.CharField(choices=[('sec', 'sec'), ('min', 'min')], default='sec', max_length=3)),
                ('notes', models.CharField(blank=True, max_length=50)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.Exercise')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='log.Log')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
