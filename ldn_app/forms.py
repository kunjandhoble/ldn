from django.forms import forms
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email', 'password')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserSignupDetails
        fields = ()