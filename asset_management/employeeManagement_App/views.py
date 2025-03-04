from django.shortcuts import render, redirect
from django.db.models import Count, Q
from .forms import EmployeeForm, DepartmentForm
from .models import Department, Employee
from assets.models import Asset
def index(request):
    """
    Displays a table of employees with filters for department and asset,
    as well as a search bar to filter by employee first or last name.
    """
    # Retrieve all departments and assets for filter drop-downs
    departments = Department.objects.all()
    assets = Asset.objects.all()
    
    # Start with all employees
    employees = Employee.objects.all()

    # Get filter parameters from GET request
    department_id = request.GET.get('department')
    asset_id = request.GET.get('asset')
    search_query = request.GET.get('search')

    # Filter employees by department if provided
    if department_id:
        employees = employees.filter(department__id=department_id)
    
    # Filter employees by asset if provided
    if asset_id:
        employees = employees.filter(assigned_assets__id=asset_id)
    
    # Filter by search query (checks both first and last names)
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        )
    
    context = {
        'departments': departments,
        'assets': assets,
        'employees': employees.distinct(),  # Use distinct() to prevent duplicates from join queries.
    }
    return render(request, 'index_employee.html', context)

def add_employee(request):
    """
    Renders a page with a form to add new employees.
    Also displays a table of existing employees.
    """
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_employee')
    else:
        form = EmployeeForm()
    
    # Retrieve all employees to display in the table
    employees = Employee.objects.all()
    context = {
        'form': form,
        'employees': employees,
    }
    return render(request, 'add_employee.html', context)

def add_department(request):
    """
    Renders a page with a form to add new departments.
    Also displays a table of existing departments with details and employee count.
    """
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_department')
    else:
        form = DepartmentForm()
    
    # Annotate each department with a count of related employees
    departments = Department.objects.all().annotate(employee_count=Count('employee'))  # Corrected related name

    context = {
        'form': form,
        'departments': departments,
    }
    return render(request, 'add_department.html', context)
