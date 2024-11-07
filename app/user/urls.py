"""
Url Mapping for user api
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views
from iotdevice import views as device_views

router = DefaultRouter()
router.register('device', device_views.DeviceViewSet)
app_name = 'user'

urlpatterns = [
    path('create', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('person/', views.ManageUserView.as_view(), name='person'),
    path('', include(router.urls)),
]
