from django.shortcuts import render, redirect
from .forms import HRSignupForm

# accounts/views.py
from django.shortcuts import render, redirect
from .forms import HRSignupForm, EmployeeSignupForm
from django.contrib.auth import login

def hr_signup(request):
    if request.method == 'POST':
        form = HRSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_hr = True  # Mark as HR
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('company:dashboard')  # Or 'company:dashboard'
    else:
        form = HRSignupForm()
    return render(request, 'accounts/signup_hr.html', {'form': form})

def employee_signup(request):
    if request.method == 'POST':
        form = EmployeeSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_employee = True  # Mark as Employee
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('employee_portal:employee_dashboard')  # Or your preferred page
    else:
        form = EmployeeSignupForm()
    return render(request, 'accounts/signup_employee.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

# accounts/views.py
from django.contrib.auth.decorators import login_required

@login_required
def post_login_redirect(request):
    user = request.user

    # Send to employee dashboard
    if getattr(user, 'is_employee', False):
        return redirect('employee_portal:employee_dashboard')

    # Send to HR dashboard
    if getattr(user, 'is_hr', False):
        return redirect('company:dashboard')

    # If no role, log out to avoid redirect loop
    from django.contrib.auth import logout
    logout(request)
    return redirect(reverse('account_login'))
