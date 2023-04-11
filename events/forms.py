from django import forms
from .models import Event
import pytz
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError


    


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'price', 'time','users',"created_by"]
        exclude = ['users',"created_by"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    def clean_time(self):
        time = self.cleaned_data['time']
        if time < timezone.now() + timezone.timedelta(hours=1):
            raise forms.ValidationError('Please make sure that the time is at least 1 hour away from now.')
        return time