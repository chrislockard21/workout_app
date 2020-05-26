from django import forms
from .models import OneRepMax
from workout.models import ExerciseByGroup

unit_choices = (
    ('lbs', 'lbs'),
    ('kg', 'kg'),
)

class OneRepMaxForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(queryset=ExerciseByGroup.objects.all().order_by('exercise_name'), widget=forms.Select(attrs={'class': 'form-control'}))
    weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=0)
    unit = forms.CharField(widget=forms.Select(choices=unit_choices, attrs={'class': 'form-control'}))

    class Meta:
        model = OneRepMax
        fields = (
            'exercise',
            'weight',
            'unit',
        )
