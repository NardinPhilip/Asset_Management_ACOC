from .models import Department, Employee,EmployeesAssignedToAssets
from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Department Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Department Description',
                'rows': 3  # Adjust the height of the textarea
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Department Location'
            }),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [ 'nationalID', 'first_name', 'last_name', 'department', 'job_title', 'hire_date']
        widgets = {
            'nationalID': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'National Id'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Last Name'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Job Title'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
        }


# Optional: Form to assign an asset to an employee.
class EmployeesAssignedToAssetsForm(forms.ModelForm):
    class Meta:
        model = EmployeesAssignedToAssets
        fields = ['employee', 'asset']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'asset': forms.Select(attrs={'class': 'form-control'}),
        }
