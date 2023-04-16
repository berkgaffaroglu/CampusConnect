from django import forms
from .models import Event
from django.utils import timezone
from social_clubs.models import SocialClub
class CreateEventForm(forms.ModelForm):
     

    social_club = forms.ModelChoiceField(queryset=SocialClub.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'price', 'time','users',"created_by", "maximum_people", "social_club" 
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
    
    def check_if_manager(self):
        social_club = self.cleaned_data.get('social_club')
        print(self.user)
        if self.user not in social_club.managers.all():
            raise forms.ValidationError('You must be a manager of the selected social club to create events.')
        return social_club
    
    def clean(self):
        cleaned_data = super().clean()
        self.check_if_manager()
        self.check_max_people()
        return cleaned_data