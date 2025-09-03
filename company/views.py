from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import Employee, Attendance, Leave, Subscription, Company
from django import forms
from django.utils import timezone
from .forms import CompanyForm


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'position']



from django.shortcuts import redirect

@login_required
def dashboard(request):
    user = request.user

    # If user is employee, redirect to employee dashboard
    if hasattr(user, 'employee'):
        return redirect('employee_portal:employee_dashboard')

    # If user is HR (has a company), show HR dashboard
    company = user.companies.first()
    if company:
        activities = Leave.objects.filter(company=company, status='Pending')[:3]
        stats = {
            'employees': Employee.objects.filter(company=company).count(),
            'projects': 3,  # Static for now
            'attendances': Attendance.objects.filter(company=company, date=timezone.now().date()).count()
        }
        return render(request, 'company/dashboard.html', {
            'default_activities': activities,
            'default_stats': stats
        })

    # If neither HR nor employee, redirect to company home or login page
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

@login_required
def attendance(request):
    company = request.user.companies.first()
    if not company:
        return JsonResponse({'success': False, 'message': 'No company found'}, status=400)

    employees = Employee.objects.filter(company=company)

    if request.method == 'POST':
        for employee in employees:
            status = request.POST.get(f'attendance_{employee.id}')  # match your input names!
            if status:
                Attendance.objects.update_or_create(
                    company=company,
                    employee=employee,
                    date=timezone.now().date(),
                    defaults={'status': status}
                )
        return JsonResponse({'success': True})

    return render(request, 'company/attendance.html', {'employees': employees, 'today': timezone.now()})
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
    subscription = Subscription.objects.filter(company=company, active=True).first()
    plans = [
        {'name': 'Free', 'price': '$0', 'features': ['Up to 10 employees', 'Basic support']},
        {'name': 'Pro', 'price': '$99/month', 'features': ['Up to 50 employees', 'Priority support', 'Advanced reporting']},
        {'name': 'Enterprise', 'price': 'Contact us', 'features': ['Unlimited employees', 'Dedicated support', 'Custom integrations']},
    ]
    return render(request, 'company/subscription.html', {'subscription': subscription, 'plans': plans})

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
