from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta

class Company(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies'
    )
    address = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    first_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
from datetime import date

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
    
    @property
    def attendances_today(self):
        return self.attendances.filter(date=date.today()).first()

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

# your_app/models.py
from django.db import models
from django.utils import timezone
# Make sure to import your Company and Employee models
# from your_accounts_app.models import Company, Employee 

# New Model for Company-specific settings
class AttendanceSettings(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='attendance_settings')
    shift_start_time = models.TimeField(default='09:30:00')
    late_grace_period_minutes = models.PositiveIntegerField(default=15, help_text="Grace period in minutes before marking as late.")
    half_day_cutoff_time = models.TimeField(default='12:00:00', help_text="Clock-ins after this time are suggested as Half Day.")

    def __str__(self):
        return f"Attendance Settings for {self.company.name}"

# Updated Attendance Model to handle requests and approval
class Attendance(models.Model):
    ATTENDANCE_TYPE_CHOICES = [
        ('On Time', 'On Time'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('Absent', 'Absent'),
        ('Holiday', 'Holiday'),
        ('Leave', 'Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    clock_in_time = models.TimeField(null=True, blank=True)
    clock_out_time = models.TimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    attendance_type = models.CharField(max_length=10, choices=ATTENDANCE_TYPE_CHOICES, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} on {self.date} - {self.attendance_type or 'Not Recorded'}"

class Leave(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Subscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="subscriptions")
    plan =models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,related_name="subscriptions")
    active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = date.today()
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=30)  # Default 1 month plan
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"



# Add these new models to your existing models.py

class Notification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"

class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ('national', 'National Holiday'),
        ('company', 'Company Holiday'),
        ('regional', 'Regional Holiday'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays')
    name = models.CharField(max_length=100)
    date = models.DateField()
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default='company')
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)  # for yearly recurring holidays
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('company', 'date', 'name')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} - {self.date}"

class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('notification', 'employee')




# hr_notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminToHRNotificationAdmin(models.Model):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='admin_to_hr_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} to {self.company.name}"

    
