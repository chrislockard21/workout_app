from django.db import models
from django.contrib.auth.models import User
from workout.models import ExerciseByGroup

unit_choices = (
    ('lbs', 'lbs'),
    ('kg', 'kg'),
)

# Create your models here.
class OneRepMax(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.OneToOneField(ExerciseByGroup, on_delete=models.CASCADE, unique=True)
    weight = models.FloatField(blank=False)
    unit = models.CharField(max_length=3, choices=unit_choices, default='lbs')

    def __str__(self):
        return '{} - {}'.format(self.exercise, self.weight)
