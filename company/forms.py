from django import forms
from .models import Company, Employee, EmployeeDocument, EmployeeBankDetail, EmployeeAadhaarDetail

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter company name'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'position',  'employment_status', 'leaving_reason', 'leaving_date']

class FireEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['leaving_reason', 'leaving_date']
        widgets = {
            'leaving_reason': forms.Textarea(attrs={'rows': 3}),
            'leaving_date': forms.DateInput(attrs={'type': 'date'}),
        }

class EmployeeCreateForm(EmployeeForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['document_name', 'document_file']

class EmployeeBankForm(forms.ModelForm):
    class Meta:
        model = EmployeeBankDetail
        fields = ['account_number', 'bank_name', 'ifsc_code', 'branch']

class EmployeeAadhaarForm(forms.ModelForm):
    class Meta:
        model = EmployeeAadhaarDetail
        fields = ['aadhaar_number', 'document_file']
