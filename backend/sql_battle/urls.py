from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django Admin перенесён на /django-admin/
    path('', include('api.urls')),  # API без префикса — как ожидает фронтенд
]
