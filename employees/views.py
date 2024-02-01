from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Employee, Employee_information, Department, Position, Internal_permission, External_permission, \
    DeactivationLog

from .forms import EmployeeForm, EmployeeInformationForm, DeactivationLogForm

from datetime import date


def valid_employees(request):
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    if order == 'desc':
        sort_by = '-' + sort_by

    employees = Employee.objects.filter(verification=Employee.VERIFICATION_ACTIVE).prefetch_related(
        'employee_information').order_by(sort_by)

    return render(request, 'employees/active_employees.html', {
        'employees': employees
    })


def view_employee(request, id):
    employee = get_object_or_404(Employee, pk=id)
    employee_information = get_object_or_404(Employee_information, employee=employee)
    deactivationlog = get_object_or_404(DeactivationLog, employee=employee)
    department = employee.department
    position = employee.position

    context = {
        'employee': employee,
        'employee_information': employee_information,
        'department': department,
        'position': position,
        'deactivationlog': deactivationlog
    }
    return render(request, 'employees/view_employees.html', context)


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            new_employee = form.save()
            return render(request, 'employees/add.html', {
                'form': EmployeeForm(),
                'success': True
            })
        else:
            return render(request, 'employees/add.html', {
                'form': form
            })
    else:
        form = EmployeeForm()
        return render(request, 'employees/add.html', {
            'form': form
        })


def add_employee_information(request):
    if request.method == 'POST':
        form = EmployeeInformationForm(request.POST)
        if form.is_valid():
            new_employee_information = form.save()
            return render(request, 'employees/add.html', {
                'form': EmployeeInformationForm(),
                'success': True
            })
        else:
            return render(request, 'employees/add.html', {
                'form': form
            })
    else:
        form = EmployeeInformationForm()
        return render(request, 'employees/add.html', {
            'form': form
        })


def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee_information = get_object_or_404(Employee_information, employee=employee)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        info_form = EmployeeInformationForm(request.POST, instance=employee_information)
        if form.is_valid() and info_form.is_valid():
            form.save()
            info_form.save()
            return redirect('active_employees')
    else:
        form = EmployeeForm(instance=employee)
        info_form = EmployeeInformationForm(instance=employee_information)

    return render(request, 'employees/edit.html', {
        'form': form,
        'info_form': info_form,
        'employee': employee
    })


def delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    deactivationlog = get_object_or_404(DeactivationLog, employee=employee)

    if request.method == 'POST':
        form = DeactivationLogForm(request.POST, instance=deactivationlog)
        if form.is_valid():
            form.save()
            employee.verification = Employee.VERIFICATION_INACTIVE
            employee.save()
            return redirect('inactive_employees')

    form = DeactivationLogForm(instance=deactivationlog)

    return render(request, 'employees/deactivate_employee.html', {
        'form': form,
        'employee': employee
    })


def inactive_employees(request):
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    if order == 'desc':
        sort_by = '-' + sort_by

    employees = Employee.objects.filter(verification=Employee.VERIFICATION_INACTIVE).order_by(sort_by)

    return render(request, 'employees/inactive_employees.html', {
        'employees': employees
    })


@require_POST
def reactivate_employee(request, id):
    employee = get_object_or_404(Employee, pk=id)
    employee.verification = Employee.VERIFICATION_ACTIVE
    employee.save()
    return redirect('inactive_employees')


def index(request):
    today = date.today()
    employees_birthday_this_month = Employee_information.objects.filter(
        date_of_birth__month=today.month
    ).select_related('employee').order_by('date_of_birth__day')

    # Pass the employees to the template
    return render(request, 'employees/index.html', {
        'employees_birthday_this_month': employees_birthday_this_month
    })
