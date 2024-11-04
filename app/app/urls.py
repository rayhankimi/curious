from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.contrib import admin
from django.urls import path, include

from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path(
        'api/schema',
        SpectacularAPIView.as_view(),
        name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(),
        name='api-docs'),
    path('api/user/', include('user.urls')),
    path('api/device/', include('iotdevice.urls')),
]
