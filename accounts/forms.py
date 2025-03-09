from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=True)
    company = forms.CharField(max_length=100, required=False)
    job_title = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    theme_preference = forms.ChoiceField(
        choices=[
            ('system', 'System Default'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        initial='system',
        required=True
    )
    notification_preferences = forms.MultipleChoiceField(
        choices=[
            ('email_updates', 'Email Updates'),
            ('product_news', 'Product News'),
            ('security_alerts', 'Security Alerts'),
            ('usage_reports', 'Usage Reports'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'company', 
            'job_title', 'phone', 'bio', 'notification_preferences', 'theme_preference'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['theme_preference'].initial = self.instance.theme_preference
            
            # Initialize notification preferences from the stored JSON
            if self.instance.notification_preferences:
                self.fields['notification_preferences'].initial = [
                    pref for pref, enabled in 
                    self.instance.notification_preferences.items() 
                    if enabled
                ]
