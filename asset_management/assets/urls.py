from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication URLs
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Main Pages
    path('index/', views.index, name='index'),
    path('branch_list/', views.branch_list, name='branch_list'),
    path('category_list/', views.category_list, name='category_list'),

    # Branch URLs
    path('add-branch/', views.add_branch, name='add_branch'),
    path('add-branch/<int:branch_id>/', views.add_branch, name='add_branch'),
    path('edit-branch/<int:branch_id>/', views.edit_branch, name='edit_branch'),
    path('delete-branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('restore-branch/<int:branch_id>/', views.restore_branch, name='restore_branch'),
    path('review-branch/<int:branch_id>/', views.review_category, name='review_branch'),
 
    # Category URLs
    path('add-category/', views.add_category, name='add_category'),
    path('add-category/<int:category_id>/', views.add_category, name='add_category'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('restore-category/<int:category_id>/', views.restore_category, name='restore_category'),
    path('review-category/<int:category_id>/', views.review_category, name='review_category'),

    # Asset Management URLs
    path('generate-asset/', views.generate_asset, name='generate_asset'),
    path('asset-management/', views.asset_management, name='asset_management'),
    path('generate-report/', views.generate_report, name='generate_report'),

    # Audit URLs
    path('start_audit/', views.start_audit, name='start_audit'),
    path('scan_qr_code/', views.scan_qr_code, name='scan_qr_code'),
    path('end_audit/', views.end_audit, name='end_audit'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)