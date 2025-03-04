import assets.models
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # New field
    location = models.ForeignKey(assets.models.Branch, max_length=255, blank=True, null=True, on_delete=models.CASCADE)  # New field

    def __str__(self):
        return self.name


class Employee(models.Model):
    nationalID = models.IntegerField(primary_key= True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class EmployeesAssignedToAssets(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assigned_assets")
    asset = models.ForeignKey(assets.models.Asset, on_delete=models.CASCADE, related_name="assigned_employees")

    class Meta:
        unique_together = ('employee', 'asset')

    def __str__(self):
        return f"{self.employee} assigned to {self.asset}"
