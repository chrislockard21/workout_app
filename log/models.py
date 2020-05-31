from django.db import models
from workout.models import Workout, Exercise, ExerciseByGroup
from django.urls import reverse
from django.contrib.auth.models import User

difficulty_choices = (
    ('E', 'Easy'),
    ('M', 'In the middle'),
    ('H', 'Hard')
)

unit_choices = (
    ('lbs', 'lbs'),
    ('kg', 'kg'),
)

distance_choices = (
    ('mi', 'mi'),
    ('km', 'km')
)

time_choices = (
    ('sec', 'sec'),
    ('min', 'min')
)

# Create your models here.
class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=6)

    def get_absolute_url(self):
        kwargs = {
            'log_pk': self.id,
        }
        return reverse('log:log_detail', kwargs=kwargs)

    def __str__(self):
        return '{}: {}'.format(self.workout, self.created_at)

class Set(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Lifting set info
    reps = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=3, choices=unit_choices, default='lbs')
    difficulty = models.CharField(max_length=1, choices=difficulty_choices, default='Easy')

    # General notes
    notes = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return '{}: set'.format(self.exercise)

class LogHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} history: {}'.format(self.workout, self.created_at.date())

class SetHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log_history = models.ForeignKey(LogHistory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Stores the built in exercise. Doing this instead of the user created
    # exercise because I do not want a delete to be able to delete the history
    exercise = models.ForeignKey(ExerciseByGroup, on_delete=models.CASCADE)

    # Lifting set info
    reps = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=3, choices=unit_choices, default='lbs')
    difficulty = models.CharField(max_length=1, choices=difficulty_choices, default='Easy')

    # General notes
    notes = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return '{}: {}'.format(self.exercise.exercise_name, self.created_at)
