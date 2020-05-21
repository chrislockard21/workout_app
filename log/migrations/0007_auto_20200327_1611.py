# Generated by Django 2.0.6 on 2020-03-27 20:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('log', '0006_auto_20200312_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workout', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='sethistory',
            name='log_history',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='log.LogHistory'),
            preserve_default=False,
        ),
    ]
