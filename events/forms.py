from django import forms
from .models import Event, EventImage
from django.utils import timezone
from social_clubs.models import SocialClub


class EventImageForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = EventImage
        fields = ('images',)

class CreateEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['social_club'].queryset = SocialClub.objects.filter(managers=self.user)
        
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'price', 'time','users',"created_by", "maximum_people", "social_club" 
                  ]
        exclude = ['users',"created_by"]
        widgets = {
            'social_club': forms.Select(attrs={'class': 'form-control form-control-lg','style':"font-size:2rem;"}),
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
    
    def check_if_manager(self):
        social_club = self.cleaned_data.get('social_club')

        try:
            if self.user not in social_club.managers.all():
                raise forms.ValidationError('You must be a manager of the selected social club to create events.')
        except AttributeError:
            raise forms.ValidationError('Please select one of the social clubs.')
        return social_club
    
    def clean(self):
        cleaned_data = super().clean()
        
        self.check_if_manager()
        self.check_max_people()
        return cleaned_data