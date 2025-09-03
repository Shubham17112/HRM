from django import forms

class GenerateLinkForm(forms.Form):
    expiry_hours = forms.IntegerField(min_value=1, initial=24, help_text='Expiry in hours')
    invited_email = forms.EmailField(required=False, help_text='Optional: email to prefill in register form')

class OnboardingForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    position = forms.CharField(max_length=100, required=False)
