from django import forms
from .models import Event
from django.utils import timezone

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'price', 'time','users',"created_by", "maximum_people"
                  ]
        exclude = ['users',"created_by"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'maximum_people':forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 3})
        }
    def clean_time(self):
        time = self.cleaned_data['time']
        if time < timezone.now() + timezone.timedelta(hours=1):
            raise forms.ValidationError('Please make sure that the time is at least 1 hour away from now.')
        return time
    
    def check_max_people(self):
        max_people = self.cleaned_data['maximum_people']
        if max_people < 3:
            raise forms.ValidationError('Please make sure that the count of maximum people that can attend must be 3 or higher!')
        return max_people