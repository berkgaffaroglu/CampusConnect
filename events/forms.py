from django import forms
from .models import Event

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'price', 'time','users',"created_by"]
        exclude = ['users',"created_by"]
        widgets = {
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }