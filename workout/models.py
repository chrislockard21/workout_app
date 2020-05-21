from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse

GROUP_CHOICES = (
    ('CHEST', 'CHEST'),
    ('BACK', 'BACK'),
    ('ARMS', 'ARMS'),
    ('LEGS', 'LEGS'),
    ('ABS', 'ABS'),
    ('SHOULDERS', 'SHOULDERS'),
)

# Create your models here.
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_name = models.CharField(max_length=30)
    workout_desc = models.TextField(max_length=300)

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
        }
        return reverse('workout:workout_detail', kwargs=kwargs)

    def __str__(self):
        return self.workout_name

class ExerciseByGroup(models.Model):
    type = models.CharField(max_length=15, choices=GROUP_CHOICES)
    exercise_name = models.CharField(max_length=50)

    def __str__(self):
        return self.exercise_name

class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseByGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.exercise.exercise_name
