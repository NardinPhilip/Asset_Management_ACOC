# asset_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns...
    path('', views.index, name='index'),
    path('add-branch/', views.add_branch, name='add_branch'),
    path('add-category/', views.add_category, name='add_category'),
    path('generate-asset/', views.generate_asset, name='generate_asset'),
    path('asset-management/', views.asset_management, name='asset_management'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('asset-management/branches/', views.view_branches, name='view-branches'),
    path('asset-management/categories/', views.view_categories, name='view-categories'),
    path('asset-management/assets/', views.view_assets, name='view-assets'),
    path('start_audit/', views.start_audit, name='start_audit'),
    path('scan_qr_code/', views.scan_qr_code, name='scan_qr_code'),
    path('end_audit/', views.end_audit, name='end_audit'),
    path('edit_branch/<int:branch_id>/', views.edit_branch, name='edit_branch'),
    path('delete_branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category')
    
]
