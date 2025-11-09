from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import Employee, Attendance, Leave, Subscription, Company, AdminToHRNotificationAdmin
from django import forms
from django.utils import timezone
from .forms import CompanyForm

from django.db.models import Count, Q
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
import calendar
from .models import Employee, Attendance, Leave, Subscription, Company, Notification, Holiday, NotificationRead, SubscriptionPlan


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'position']



from django.shortcuts import redirect


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from .models import Employee, Attendance, Leave, Notification, Holiday
from company.models import AdminToHRNotificationAdmin

@login_required
def dashboard(request):
    user = request.user
    # If user is employee, redirect to employee dashboard
    if hasattr(user, 'employee'):
        return redirect('employee_portal:employee_dashboard')
    try:
        
        company = user.companies.first()  # if multiple, you may adjust logic
        print('inside the try block of dashboard')
    except Company.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    company = getattr(user, 'name', None)
    if not company:
        return redirect("accounts:hr_signup")
        
    admin_notifications = company.admin_to_hr_notifications.all().order_by('-created_at')
    print('admin_notifications:', admin_notifications)
    # If user is HR (has a company), show HR dashboard
    company = user.companies.first()
    if company:
        if request.method == 'POST':
            if 'notification_message' in request.POST:
                title = request.POST.get('notification_title', 'General Announcement')
                message = request.POST.get('notification_message')
                if message.strip():
                    Notification.objects.create(
                        company=company,
                        title=title,
                        message=message,
                        created_by=user
                    )
                    messages.success(request, 'Notification sent to all employees successfully!')
                return redirect('company:dashboard')
        
        # Current date and statistics
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        total_employees = Employee.objects.filter(company=company, is_active=True).count()
        present_today = Attendance.objects.filter(
            employee__company=company,
            date=today, 
            attendance_type='On Time'
        ).count()

        total_attendance_today = Attendance.objects.filter(employee__company=company, date=today).count()
        attendance_percentage = round((present_today / total_employees * 100) if total_employees > 0 else 0, 1)

        pending_leaves = Leave.objects.filter(company=company, status='Pending').count()
        approved_leaves_today = Leave.objects.filter(
            company=company, 
            status='Approved',
            from_date__lte=today,
            to_date__gte=today
        ).count()

        monthly_attendance = Attendance.objects.filter(
            employee__company=company,
            date__month=current_month,
            date__year=current_year
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(attendance_type='On Time')),
            absent=Count('id', filter=Q(attendance_type='Absent'))
        )

        recent_leaves = Leave.objects.filter(employee__company=company).order_by('-id')[:5]
        recent_attendance = Attendance.objects.filter(employee__company=company).order_by('-date', '-id')[:5]

        activities = []
        for leave in recent_leaves:
            activities.append({
                'type': 'leave',
                'description': f"{leave.employee.name} applied for leave ({leave.status.lower()})",
                'time': leave.from_date.strftime('%b %d, %Y'),
                'status': leave.status.lower(),
                'icon_class': 'blue' if leave.status == 'Pending' else ('green' if leave.status == 'Approved' else 'yellow')
            })
        
        for att in recent_attendance[:3]:
            activities.append({
                'type': 'attendance',
                'description': f"{att.employee.name} marked {att.attendance_type.lower()}",
                'time': att.date.strftime('%b %d, %Y'),
                'status': att.attendance_type.lower(),
                'icon_class': 'green' if att.attendance_type == 'On Time' else 'yellow'
            })

        activities = sorted(activities, key=lambda x: x['time'], reverse=True)[:6]

        quick_stats = [
            {
                'name': 'Today\'s Attendance',
                'value': f'{attendance_percentage}%',
                'percentage': attendance_percentage
            },
            {
                'name': 'Monthly Productivity',
                'value': '78%',
                'percentage': 78
            },
            {
                'name': 'Leave Approval Rate',
                'approved_leaves': Leave.objects.filter(company=company,status='Approved').count(),
                'total_leaves': Leave.objects.filter(company=company).count(),
            }
        ]

        if quick_stats[2]['total_leaves'] > 0:
            approval_rate = round((quick_stats[2]['approved_leaves'] / quick_stats[2]['total_leaves']) * 100, 1)
        else:
            approval_rate = 0

        quick_stats[2]['value'] = f'{approval_rate}%'
        quick_stats[2]['percentage'] = approval_rate

        recent_notifications = Notification.objects.filter(company=company, is_active=True)[:5]

        # -----------------------------
        # Calendar data for the template
        # -----------------------------
        # Fetch holidays for this month
        holidays = Holiday.objects.filter(company=company, date__year=current_year, date__month=current_month)

        # Fetch attendance for this month
        attendances = Attendance.objects.filter(
            employee__company=company,
            date__year=current_year,
            date__month=current_month
        )

        # Create mapping for holidays and attendance
        holiday_map = {h.date.strftime("%Y-%m-%d"): h.name for h in holidays}
        attendance_map = {a.date.strftime("%Y-%m-%d"): a.attendance_type for a in attendances}

        context = {
            'company': company,
            'total_employees': total_employees,
            'present_today': present_today,
            'total_attendance_today': total_attendance_today,
            'attendance_percentage': attendance_percentage,
            'pending_leaves': pending_leaves,
            'approved_leaves_today': approved_leaves_today,
            'monthly_attendance': monthly_attendance,
            'recent_activities': activities,
            'quick_stats': quick_stats,
            'recent_notifications': recent_notifications,
            'today': today,
            'current_year': current_year,
            'current_month': current_month,
            'holiday_map': holiday_map,
            'attendance_map': attendance_map,
            'admin_notifications': admin_notifications,
        }

        return render(request, 'company/dashboard.html', context)

    return redirect('company:company_home')

from django.shortcuts import redirect

def company_home(request):
    if request.user.is_authenticated:
        print('user is authenticated')

        # If user is employee, redirect to employee dashboard
        if hasattr(request.user, 'employee'):
            
            return redirect('employee_portal:employee_dashboard')

        # If user is HR (has a company), redirect to company dashboard
        if request.user.companies.exists():
            print('user has a company')
            return redirect('company:dashboard')

        if request.method == 'POST':
            print('post request received')
            form = CompanyForm(request.POST)
            if form.is_valid():
                company = form.save(commit=False)
                company.owner = request.user
                company.save()
                return redirect('company:dashboard')
        else:
            form = CompanyForm()

        return render(request, 'company/landing.html', {'form': form})

    return render(request, 'company/landing.html')


@login_required
def employees(request):
    company = request.user.companies.first()
    if not company:
        return redirect('company:company_home')

    current_employees = Employee.objects.filter(company=company, is_active=True)
    past_employees = Employee.objects.filter(company=company, is_active=False)

    return render(request, 'company/employees.html', {
        'current_employees': current_employees,
        'past_employees': past_employees
    })

@login_required
def employee_detail(request, employee_id):
    company = request.user.companies.first()
    if not company:
        return redirect('company:company_home')

    # Get employee from same company
    employee = Employee.objects.filter(company=company, id=employee_id).first()
    if not employee:
        return redirect('company:employees')  # If not found, go back to list

    # Related data
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')
    leaves = Leave.objects.filter(employee=employee).order_by('-from_date')

    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'leaves': leaves
    }
    return render(request, 'company/employee_detail.html', context)
from django.http import JsonResponse


def attendance(request):
    company = request.user.companies.first()

    if not company:
        return JsonResponse({'success': False, 'message': 'No company found'}, status=400)

    employees = Employee.objects.filter(company=company)

    if request.method == 'POST':
        for employee in employees:
            status = request.POST.get(f'attendance_{employee.id}')  # match your input names
            if status:
                Attendance.objects.update_or_create(
                    employee=employee,
                    date=timezone.now().date(),
                    defaults={'attendance_type': status}
                )
        return JsonResponse({'success': True})

    return render(request, 'company/attendance.html', {'employees': employees, 'today': timezone.now().date()})


from django.shortcuts import render, redirect, get_object_or_404


@login_required
def leaves(request):
    company = request.user.companies.first()
    if not company:
        return redirect('company:company_home')

    leaves = Leave.objects.filter(company=company)
    status_filter = request.GET.get('status', '')
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave = get_object_or_404(Leave, id=leave_id, company=company)
        leave.status = action
        leave.save()
        return redirect('leaves')

    # ✅ variable matches template now
    return render(request, 'company/leaves.html', {'leave_requests': leaves})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # or use @csrf_protect and send CSRF token in fetch headers
def update_leave_status(request, id, status):
    if request.method == "POST":
        try:
            leave = Leave.objects.get(id=id)
            leave.status = status.capitalize()  # e.g., 'Approved' or 'Rejected'
            leave.save()
            return JsonResponse({'success': True})
        except Leave.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Leave not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def subscription(request):
    company = request.user.companies.first()
    if not company:
        return redirect('company:company_home')

    # check active subscription
    active_subscription = Subscription.objects.filter(company=company, active=True).first()

    plans = SubscriptionPlan.objects.all()
    return render(request, "company/subscription.html", {
        "plans": plans,
        "active_subscription": active_subscription
    })

def logout(request):
    auth_logout(request)
    return render(request, 'company/landing.html')

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth import get_user_model
User = get_user_model()

from .forms import EmployeeCreateForm  # make sure you're using the form with username/password

from .forms import EmployeeCreateForm
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def add_employee(request):
    company = request.user.companies.first()
    if not company:
        return redirect('company_home')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists. Please choose another.')
                return render(request, 'company/employee_form.html', {'form': form})

            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=username,
                password=password,
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['name']
            )
            user.is_employee = True  # Set employee flag
            user.save()

            employee = form.save(commit=False)
            employee.company = company
            employee.user = user
            employee.save()

            return redirect('company:employees')

        else:
            print(form.errors)

    else:
        form = EmployeeCreateForm()

    return render(request, 'company/employee_form.html', {'form': form})

@login_required
def edit_employee(request, employee_id):
  

    return render(request, 'company/employee_form.html')

from django.contrib.auth import login
from .forms import FireEmployeeForm

def fire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = FireEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            emp = form.save(commit=False)
            emp.is_active = False
            emp.employment_status = "past"
            emp.save()
            return redirect('company:employees')
    else:
        form = FireEmployeeForm(instance=employee)
    return render(request, 'company/fire_employee.html', {'form': form, 'employee': employee})




## calendar code from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Holiday
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Holiday
import datetime



@login_required
def holiday_calendar(request):
    company = request.user.companies.first()
    if not company:
        return redirect('company:company_home')
    
    if request.method == 'POST':
        if 'add_holiday' in request.POST:
            name = request.POST.get('holiday_name')
            date = request.POST.get('holiday_date')
            holiday_type = request.POST.get('holiday_type', 'company')
            description = request.POST.get('description', '')

            if name and date:
                Holiday.objects.create(
                    company=company,
                    name=name,
                    date=date,
                    holiday_type=holiday_type,
                    description=description
                )
                messages.success(request, 'Holiday added successfully!')

        return redirect('company:holiday_calendar')

    # GET request: fetch holidays and pass to template
    holidays_qs = Holiday.objects.filter(company=company)
    holidays = []
    for h in holidays_qs:
        holidays.append({
            'date': h.date.strftime('%Y-%m-%d'),
            'name': h.name,
            'holiday_type': h.holiday_type,
            'description': h.description or ''
        })

    # Prepare attendance map
    current_year = datetime.date.today().year
    start_date = datetime.date(current_year, 1, 1)
    end_date = datetime.date(current_year, 12, 31)

    attendances = Attendance.objects.filter(
        employee__company=company,
        date__range=(start_date, end_date)
    )

    attendance_map = {}
    for att in attendances:
        attendance_map[att.date.strftime('%Y-%m-%d')] = att.attendance_type

    return render(request, 'company/holiday_calendar.html', {
        'holidays': holidays,                 # List of holiday dicts
        'attendance_map': attendance_map,     # Dictionary for attendance by date
        'current_year': current_year,
        'company': company,
    })


def create_default_indian_holidays(company, year):
    """Create default Indian holidays for the year"""
    default_holidays = [
        {'name': 'New Year\'s Day', 'date': f'{year}-01-01', 'type': 'national'},
        {'name': 'Republic Day', 'date': f'{year}-01-26', 'type': 'national'},
        {'name': 'Independence Day', 'date': f'{year}-08-15', 'type': 'national'},
        {'name': 'Gandhi Jayanti', 'date': f'{year}-10-02', 'type': 'national'},
        {'name': 'Diwali', 'date': f'{year}-11-01', 'type': 'national'},  # Approximate date
        {'name': 'Holi', 'date': f'{year}-03-13', 'type': 'national'},    # Approximate date
        {'name': 'Dussehra', 'date': f'{year}-10-15', 'type': 'national'}, # Approximate date
    ]
    
    for holiday_data in default_holidays:
        Holiday.objects.get_or_create(
            company=company,
            name=holiday_data['name'],
            date=holiday_data['date'],
            defaults={
                'holiday_type': holiday_data['type'],
                'description': f'Default {holiday_data["type"]} holiday'
            }
        )

# API view for calendar data
@login_required
def get_calendar_data(request):
    company = request.user.companies.first()
    if not company:
        return JsonResponse({'error': 'No company found'}, status=400)
    
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    # Get holidays for the month
    holidays = Holiday.objects.filter(
        company=company,
        date__year=year,
        date__month=month
    ).values('date', 'name', 'holiday_type')
    
    # Convert to list for JSON response
    holiday_list = []
    for holiday in holidays:
        holiday_list.append({
            'date': holiday['date'].strftime('%Y-%m-%d'),
            'name': holiday['name'],
            'type': holiday['holiday_type']
        })
    
    return JsonResponse({
        'holidays': holiday_list,
        'sundays': get_sundays_in_month(int(year), int(month))
    })

def get_sundays_in_month(year, month):
    """Get all Sundays in a given month"""
    sundays = []
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        if week[6] != 0:  # Sunday is at index 6, 0 means no date
            sundays.append(f"{year}-{month:02d}-{week[6]:02d}")
    return sundays



# Optional: Only allow HR/admin users
def is_hr_or_admin(user):
    return user.is_staff  # Adjust according to your HR logic


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
import json

@login_required
@user_passes_test(is_hr_or_admin)
@csrf_exempt
def update_attendance(request):
    """
    Employer can manually change attendance type and approve it.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            attendance_id = data.get('attendance_id')
            attendance_type = data.get('attendance_type')

            attendance = Attendance.objects.get(id=attendance_id)
            attendance.attendance_type = attendance_type
            attendance.approved = True 
            attendance.save()
            
            return JsonResponse({'success': True})
        except Attendance.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Attendance not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

login_required
from django.views.decorators.csrf import csrf_exempt
login_required
import json
@csrf_exempt  # needed for JSON POST via fetch
def update_attendance(request):
    print('update_attendance called')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            attendance_id = data.get('attendance_id')
            attendance_type = data.get('attendance_type')

            attendance = Attendance.objects.get(id=attendance_id)
            attendance.attendance_type = attendance_type
            attendance.approved = True  # mark as approved
            attendance.save()

            return JsonResponse({'success': True})
        except Attendance.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Attendance not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


from django.http import HttpResponse, HttpResponseForbidden
import csv
from datetime import date

@login_required
def export_attendance_csv(request):
    user = request.user

    # Get the company where this user is the owner (HR)
    company = Company.objects.filter(owner=user).first()
    if not company:
        return HttpResponseForbidden("You are not authorized to access this data.")

    # Get month from query parameter
    month_str = request.GET.get('month')
    if not month_str:
        return HttpResponse("Month not provided", status=400)

    try:
        month_date = datetime.strptime(month_str, '%Y-%m')
    except ValueError:
        return HttpResponse("Invalid month format", status=400)

    # Get attendance records for all employees of this company in the selected month
    attendances = Attendance.objects.filter(
        employee__company=company,
        date__year=month_date.year,
        date__month=month_date.month
    ).order_by('date', 'employee__name')

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{month_str}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee Name', 'Date', 'Clock In Time', 'Clock Out Time', 'Attendance Type', 'Approved'])

    for attendance in attendances:
        writer.writerow([
            attendance.employee.name,
            attendance.date.strftime('%Y-%m-%d'),
            attendance.clock_in_time.strftime('%H:%M') if attendance.clock_in_time else '',
            attendance.clock_out_time.strftime('%H:%M') if attendance.clock_out_time else '',
            attendance.attendance_type or '',
            'Yes' if attendance.approved else 'No'
        ])

    return response
