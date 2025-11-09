from django.contrib import admin
from .models import (
    Company, Employee, EmployeeDocument, EmployeeBankDetail, EmployeeAadhaarDetail,
    AttendanceSettings, Attendance, Leave, Subscription, Notification, Holiday, NotificationRead
)
# from company.models import AdminToHRNotification  # new model

# ------------------ Company ------------------


# ------------------ Employee ------------------
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'position', 'employment_status', 'is_active')
    search_fields = ('name', 'email', 'company__name')
    list_filter = ('company', 'employment_status', 'is_active')

# ------------------ Employee Documents ------------------
@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_name', 'uploaded_at')
    search_fields = ('employee__name', 'document_name')
    list_filter = ('uploaded_at',)

# ------------------ Bank Details ------------------
@admin.register(EmployeeBankDetail)
class EmployeeBankDetailAdmin(admin.ModelAdmin):
    list_display = ('employee', 'bank_name', 'account_number', 'active', 'added_on')
    search_fields = ('employee__name', 'bank_name', 'account_number')
    list_filter = ('active', 'bank_name')

# ------------------ Aadhaar Details ------------------
@admin.register(EmployeeAadhaarDetail)
class EmployeeAadhaarDetailAdmin(admin.ModelAdmin):
    list_display = ('employee', 'aadhaar_number', 'added_on')
    search_fields = ('employee__name', 'aadhaar_number')

# ------------------ Attendance Settings ------------------
@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ('company', 'shift_start_time', 'late_grace_period_minutes', 'half_day_cutoff_time')

# ------------------ Attendance ------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'attendance_type', 'clock_in_time', 'clock_out_time', 'approved')
    search_fields = ('employee__name', 'attendance_type')
    list_filter = ('attendance_type', 'approved', 'date')

# ------------------ Leave ------------------
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'from_date', 'to_date', 'status')
    search_fields = ('employee__name', 'company__name', 'status')
    list_filter = ('status',)



# ------------------ Notification (HR → Employee) ------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('company', 'title', 'created_by', 'created_at', 'is_active')
    search_fields = ('title', 'company__name', 'created_by__username')
    list_filter = ('is_active', 'created_at')

# ------------------ Holiday ------------------
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'date', 'holiday_type', 'is_recurring')
    search_fields = ('name', 'company__name', 'holiday_type')
    list_filter = ('holiday_type', 'is_recurring', 'date')

# ------------------ Notification Read ------------------
@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ('notification', 'employee', 'read_at')
    search_fields = ('notification__title', 'employee__name')
    list_filter = ('read_at',)

# ------------------ Admin → HR Notifications ------------------
from django.contrib import admin
from .models import AdminToHRNotificationAdmin

@admin.register(AdminToHRNotificationAdmin)
class AdminToHRNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'created_by', 'created_at', 'is_read')
    search_fields = ('title', 'company__name', 'created_by__username')
    list_filter = ('is_read', 'created_at')
from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Company

# ------------------ Subscription Plan ------------------
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    ordering = ('price', 'name')
    list_per_page = 20

    def __str__(self):
        return self.name


# ------------------ Subscription Inline for Company ------------------
class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    readonly_fields = ('start_date', 'end_date')
    autocomplete_fields = ('plan',)
    show_change_link = True
    can_delete = True


# ------------------ Subscription ------------------
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'active', 'start_date', 'end_date')
    list_filter = ('active', 'plan')
    search_fields = ('company__name', 'plan__name')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    list_per_page = 25

    def get_queryset(self, request):
        """Show company & plan info efficiently"""
        qs = super().get_queryset(request)
        return qs.select_related('company', 'plan')

    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"


# ------------------ Company (with Subscriptions Inline) ------------------
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'first_login')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_active',)
    inlines = [SubscriptionInline]
