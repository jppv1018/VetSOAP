from django.contrib import admin
from django.urls import path, include
from vet.soap_service import veterinaria_service

urlpatterns = [
    path('admin/', admin.site.urls),
    path('soap/', veterinaria_service),
    path('', include('vet.urls')),
]