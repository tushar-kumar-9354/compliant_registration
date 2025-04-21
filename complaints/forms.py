from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Complaint, StatusUpdate, User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'category',
            'description',
            'image',
            'voice_note',
            'latitude',
            'longitude',
            'address'
        ]


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['new_status', 'note']
