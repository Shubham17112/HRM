# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from company.models import Company

User = get_user_model()
from django import forms

# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from company.models import Company, AttendanceSettings

User = get_user_model()

class HRSignupForm(forms.Form):
    # -------------------------------
    # COMPANY INFO
    # -------------------------------
    name = forms.CharField(
        max_length=200, required=True, label="Company Name",
        widget=forms.TextInput(attrs={
            "class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"
        })
    )
    address = forms.CharField(
        required=False, label="Address",
        widget=forms.Textarea(attrs={
            "rows": 2,
            "class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"
        })
    )
    industry = forms.ChoiceField(
        choices=[('IT', 'IT / Software'), ('Manufacturing', 'Manufacturing'), ('Healthcare', 'Healthcare')],
        required=False, label="Industry / Sector",
        widget=forms.Select(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )
    company_size = forms.ChoiceField(
        choices=[('1-10', '1–10'), ('11-50', '11–50'), ('51-200', '51–200'), ('201+', '201+')],
        required=False, label="Company Size",
        widget=forms.Select(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )
    website = forms.URLField(
        required=False, label="Website",
        widget=forms.URLInput(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )

    # -------------------------------
    # HR PERSONAL INFO
    # -------------------------------
    first_name = forms.CharField(max_length=100, required=True, label="First Name")
    last_name = forms.CharField(max_length=100, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=True, label="Phone Number")

    password = forms.CharField(
        required=True, label="Password",
        widget=forms.PasswordInput(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )
    confirm_password = forms.CharField(
        required=True, label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )

    # -------------------------------
    # ATTENDANCE SETTINGS INPUTS
    # -------------------------------
    shift_start_time = forms.TimeField(
        required=True, label="Shift Start Time",
        widget=forms.TimeInput(format='%H:%M', attrs={
            "type": "time", "class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"
        })
    )
    late_grace_period_minutes = forms.IntegerField(
        required=True, min_value=0, max_value=120, label="Late Grace Period (Minutes)",
        widget=forms.NumberInput(attrs={"class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"})
    )
    half_day_cutoff_time = forms.TimeField(
        required=True, label="Half-Day Cutoff Time",
        widget=forms.TimeInput(format='%H:%M', attrs={
            "type": "time", "class": "w-full mt-1 border border-gray-300 rounded-lg px-3 py-2"
        })
    )

    accept_terms = forms.BooleanField(required=True, label="I accept Terms & Conditions")

    # -------------------------------
    # VALIDATION
    # -------------------------------
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        cpw = cleaned_data.get("confirm_password")
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    # -------------------------------
    # SAVE LOGIC
    # -------------------------------
    def save(self, commit=True):
        data = self.cleaned_data

        # Create HR user
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.is_hr = True
        if commit:
            user.save()

        # Create the company
        company = Company.objects.create(
            name=data['name'],
            owner=user,
            address=data.get('address', ''),
            industry=data.get('industry', ''),
            company_size=data.get('company_size', ''),
            website=data.get('website', '')
        )

        # Create attendance settings from form input
        AttendanceSettings.objects.create(
            company=company,
            shift_start_time=data['shift_start_time'],
            late_grace_period_minutes=data['late_grace_period_minutes'],
            half_day_cutoff_time=data['half_day_cutoff_time']
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