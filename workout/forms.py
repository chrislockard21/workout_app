from django import forms
from .models import Workout, Exercise, ExerciseByGroup

class WorkoutCreationForm(forms.ModelForm):
    workout_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    workout_desc = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Workout
        fields = (
            'workout_name',
            'workout_desc'
        )

class ExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = (
            'exercise',
        )

    def __init__(self, *args, **kwargs):
        '''
        Overwrites the initialization for the form to accept the type
        '''
        type = kwargs.pop('type', '')
        super(ExerciseForm, self).__init__(*args, **kwargs)
        self.fields['exercise']=forms.ModelChoiceField(
            queryset=ExerciseByGroup.objects.filter(type=type),
            widget=forms.Select(attrs={'class': 'form-control'}),
            empty_label=None,
        )
