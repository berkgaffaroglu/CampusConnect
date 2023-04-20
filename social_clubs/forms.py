from django import forms
from social_clubs.models import SocialClub
class CreateSocialClubForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
    class Meta:
        model = SocialClub
        fields = ['name', "description",
                  ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        }