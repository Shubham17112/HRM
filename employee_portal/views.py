from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from company.models import Employee, Attendance, Leave, Notification
from datetime import datetime, timedelta, date
from django.utils import timezone
from .models import Attendance, AttendanceSettings, Employee

@login_required
def employee_dashboard(request):
    print('employee dashboar dhit ')
    if not hasattr(request.user, 'employee'):
        print('this employee is not in database')
        return redirect('company:dashboard')  # HR dashboard or company home

    employee = request.user.employee
    company = employee.company
    settings = company.attendance_settings  # Access AttendanceSettings
    today = date.today()
    todays_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    shift_start_time = settings.shift_start_time.strftime('%H:%M')
    grace_minutes = settings.late_grace_period_minutes
    half_day_time = settings.half_day_cutoff_time.strftime('%H:%M')
    
    # Use company and employee objects as needed
    leaves = Leave.objects.filter(employee=employee)
    attendance = Attendance.objects.filter(employee=employee)
    notifications = Notification.objects.filter(company=company, is_active=True)[:5]
    return render(request, 'employee_portal/dashboard.html', {
        'employee': employee,
        'leaves': leaves,
        'attendance': attendance,
         'company': company,
         'notifications': notifications,
          'shift_start_time': settings.shift_start_time.strftime('%H:%M'),
        'grace_period_minutes': settings.late_grace_period_minutes,
        'half_day_time': half_day_time,  
        'todays_attendance': todays_attendance,
    })
from django.contrib import messages
# your_employee_portal/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Employee, Attendance, AttendanceSettings
@login_required
def clock_in(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = timezone.now().date()
        current_time = timezone.now().time()
        reason = request.POST.get('reason', '')

        # Check if already clocked in
        if Attendance.objects.filter(employee=employee, date=today).exists():
            messages.error(request, "You have already clocked in today.")
            return redirect('employee_portal:employee_dashboard')

        # Get company settings
        settings = AttendanceSettings.objects.get(company=employee.company)
        shift_start = settings.shift_start_time

        # Calculate grace period end time
        shift_start_dt = datetime.combine(today, shift_start)
        grace_period_end_dt = shift_start_dt + timedelta(minutes=settings.late_grace_period_minutes)
        grace_period_end_time = grace_period_end_dt.time()

        # Determine attendance type (auto-selected for employer view)
        attendance_type = 'On Time'
        if current_time > settings.half_day_cutoff_time:
            attendance_type = 'Half Day'
        elif current_time > grace_period_end_time:
            attendance_type = 'Late'

        # Create Attendance record with suggested status as attendance_type
        Attendance.objects.create(
            employee=employee,
            date=today,
            clock_in_time=current_time,
            attendance_type=attendance_type,  # directly set here
            reason=reason,
            approved=False,   
        )

        messages.success(request, f"Successfully clocked in at {current_time.strftime('%I:%M %p')}.")
    return redirect('employee_portal:employee_dashboard')


@login_required
def clock_out(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = timezone.now().date()
        
        try:
            attendance_record = Attendance.objects.get(employee=employee, date=today)
            if attendance_record.clock_out_time:
                messages.error(request, "You have already clocked out today.")
            else:
                attendance_record.clock_out_time = timezone.now().time()
                attendance_record.save()
                messages.success(request, f"Successfully clocked out at {attendance_record.clock_out_time.strftime('%I:%M %p')}.")
        except Attendance.DoesNotExist:
            messages.error(request, "You did not clock in today, so you cannot clock out.")

    return redirect('employee_portal:employee_dashboard')
# Add JsonResponse to your imports at the top of the file
from django.http import JsonResponse

# ... your other views like employee_dashboard ...
@login_required
def fetch_notifications(request):
    print('fetch_notifications called')
    """
    This view returns new notifications as JSON.
    """
    if not hasattr(request.user, 'employee'):
        return JsonResponse({'status': 'error', 'message': 'User is not an employee'}, status=403)

    company = request.user.employee.company

    # Fetch the 5 most recent active notifications
    notifications = Notification.objects.filter(
        company=company, 
        is_active=True
    )[:5]

    # Format the data into a list of dictionaries
    notification_list = []
    for notif in notifications:
        notification_list.append({
            'title': notif.title,
            'message': notif.message,
            'created_at': notif.created_at.strftime('%b %d, %Y, %I:%M %p') # Formatted time
        })
    return JsonResponse({'notifications': notification_list})


@login_required
def apply_leave(request):
    if not hasattr(request.user, 'employee'):
        return redirect('company:dashboard')

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason')

        Leave.objects.create(
            employee=request.user.employee,
            company=request.user.employee.company,
            from_date=from_date,
            to_date=to_date,
            status='Pending',
            reason=reason
        )
        return redirect('employee_portal:employee_dashboard')

    return render(request, 'employee_portal/apply_leave.html')
