from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index_employee'),  # Home page of the employee app
    path('add_employee/', views.add_employee, name='add_employee'),
    path('add_department/', views.add_department, name='add_department'),
]
