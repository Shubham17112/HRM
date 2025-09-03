from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .models import EmployeeInvite

@login_required
def generate_employee_link(request):
    company = request.user.companies.first()
    if not company:
        return redirect("company:employees")

    if request.method == "POST":
        expiry_hours = int(request.POST.get("expiry", 24))  # default 24h
        invite = EmployeeInvite.objects.create(
            company=company,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(hours=expiry_hours)
        )
        link = request.build_absolute_uri(f"/self-signup/{invite.token}/")

        # return employees page with invite link
        return render(request, "company/employees.html", {
            "employees": company.employees.all(),
            "invite_link": link
        })

    return redirect("company:employees")

from django.http import HttpResponseForbidden
from company.forms import EmployeeCreateForm
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

def employee_self_register(request, token):
    try:
        invite = EmployeeInvite.objects.get(token=token)
    except EmployeeInvite.DoesNotExist:
        return render(request, "self_signup/link_expired.html")

    if invite.is_expired():
        return render(request, "self_signup/link_expired.html")

    if request.method == "POST":
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists. Please choose another.')
                return render(request, "company/employee_form.html", {"form": form})

            password = form.cleaned_data['password']
            user = User.objects.create_user(
                username=username,
                password=password,
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['name']
            )
            user.is_employee = True
            user.save()

            employee = form.save(commit=False)
            employee.company = invite.company
            employee.user = user
            employee.save()

            # invite.delete()  # invalidate link after use

            return redirect("company:employees")

    else:
        form = EmployeeCreateForm()

    return render(request, "company/employee_form.html", {"form": form})
from django.shortcuts import get_object_or_404

@login_required
def delete_invite(request, invite_id):
    invite = get_object_or_404(EmployeeInvite, id=invite_id, company=request.user.companies.first())
    invite.delete()
    return redirect("company:employees")