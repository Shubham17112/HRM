from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- change this
        on_delete=models.CASCADE,
        related_name='companies'
    )

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee'
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=50)

    # 🔹 New fields for HRM system
    is_active = models.BooleanField(default=True)  
    employment_status = models.CharField(
        max_length=10,
        choices=[('current', 'Current'), ('past', 'Past')],
        default='current'
    )
    leaving_reason = models.TextField(blank=True, null=True)
    leaving_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------- NEW MODELS -------------------

# For multiple employee documents
class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.document_name}"

# Bank details (one-to-one)
class EmployeeBankDetail(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bank_details')
    account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    branch = models.CharField(max_length=50)
    active = models.BooleanField(default=True)  # mark old accounts inactive
    added_on = models.DateTimeField(auto_now_add=True)


# Aadhaar details (one-to-one)
class EmployeeAadhaarDetail(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='aadhaar_detail')
    aadhaar_number = models.CharField(max_length=12, unique=True)
    document_file = models.FileField(upload_to='employee_aadhaar/')
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.aadhaar_number}"


class Attendance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('employee', 'date')

class Leave(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])

class Subscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=[('Free', 'Free'), ('Pro', 'Pro'), ('Enterprise', 'Enterprise')])
    active = models.BooleanField(default=True)  


