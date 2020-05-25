from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, AuthenticationForm

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username", widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'form-control'}),
        required=True
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        validators=[MinLengthValidator(10)]
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        validators=[MinLengthValidator(10)]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class CustomPasswordResetForm(PasswordResetForm):
    '''Overwrites the styles for password reset form'''
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'class':'form-control'}))

class CustomSetPasswordForm(SetPasswordForm):
    '''Overwrites the set password form'''
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
