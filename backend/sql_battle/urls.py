from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin на /django-admin/
    path('api/', include('api.urls')),  # API с префиксом /api/ — как ожидает фронтенд
]
