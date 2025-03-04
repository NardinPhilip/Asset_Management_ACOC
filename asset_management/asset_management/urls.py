from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from assets.views import login_view  # Import the login view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),  # Root URL directs to the login page
    path('assets/', include('asset_management.urls')),
    path('employees/', include('employeeManagement_App.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
