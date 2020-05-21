from django import forms
from .models import Log, Set

difficulty_choices = (
    ('E', 'Easy'),
    ('M', 'In the middle'),
    ('H', 'Hard')
)

unit_choices = (
    ('lbs', 'lbs'),
    ('kg', 'kg'),
)

class SetForm(forms.ModelForm):
    reps = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=0)
    weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=0)
    unit = forms.CharField(widget=forms.Select(choices=unit_choices, attrs={'class': 'form-control'}))
    difficulty = forms.CharField(widget=forms.Select(choices=difficulty_choices, attrs={'class': 'form-control'}))
    notes = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Set
        fields = (
            'reps',
            'weight',
            'unit',
            'difficulty',
            'notes'
        )
