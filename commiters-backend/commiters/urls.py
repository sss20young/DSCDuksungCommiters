from django.contrib import admin
from django.urls import path, include
import attendance.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('attendance.urls')),
    path('accounts/', include('allauth.urls')),
]