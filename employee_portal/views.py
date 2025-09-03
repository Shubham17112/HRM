from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from company.models import Employee, Attendance, Leave

@login_required
def employee_dashboard(request):
    print('employee dashboar dhit ')
    if not hasattr(request.user, 'employee'):
        print('this employee is not in database')
        return redirect('company:dashboard')  # HR dashboard or company home

    employee = request.user.employee
    company = employee.company

    # Use company and employee objects as needed
    leaves = Leave.objects.filter(employee=employee)
    attendance = Attendance.objects.filter(employee=employee)

    return render(request, 'employee_portal/dashboard.html', {
        'employee': employee,
        'leaves': leaves,
        'attendance': attendance,
         'company': company,
    })

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
        return redirect('employee_portal:dashboard')

    return render(request, 'employee_portal/apply_leave.html')
