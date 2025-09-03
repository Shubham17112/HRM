# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from company.models import Company

User = get_user_model()

class HRSignupForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, label="Company Name")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_hr = True  # You need a field in your custom user model for this
        if commit:
            user.save()
            Company.objects.create(
                name=self.cleaned_data['company_name'],
                owner=user
            )
        return user

class EmployeeSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_employee = True
        if commit:
            user.save()
        return user