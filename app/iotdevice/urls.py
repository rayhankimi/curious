"""
Url Mapping for the devices app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from iotdevice import views

router = DefaultRouter()
router.register('devices', views.DeviceViewSet)

app_name = 'iotdevice'

urlpatterns = [
    path('', include(router.urls)),
]