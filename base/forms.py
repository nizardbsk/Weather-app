from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm

class ProfileUpdateForm(ModelForm):
    class Meta:
        model=Profile
        fields=['username','avatar']