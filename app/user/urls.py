from django.urls import path, include
from rest_framework_nested import routers

from user import views as user_views
from iotdevice import views as device_views

# Main Router
router = routers.DefaultRouter()
router.register('device', device_views.DeviceViewSet)

# Nested Router
device_router = routers.NestedDefaultRouter(
    router,
    'device',
    lookup='device'
)
device_router.register(
    'value',
    device_views.DeviceValueViewSet,
    basename='device-value',
)

app_name = 'user'

urlpatterns = [
    path('create', user_views.CreateUserView.as_view(), name='create'),
    path('token/', user_views.CreateTokenView.as_view(), name='token'),
    path('person/', user_views.ManageUserView.as_view(), name='person'),
    path('', include(router.urls)),
    path('', include(device_router.urls)),
]
