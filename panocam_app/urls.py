from django.urls import include, path
from rest_framework import routers
from . import api_methods
from . import views, api_models

router = routers.DefaultRouter()
router.register('ConfigurationViewSet', api_models.ConfigurationViewSet)
router.register('CameraViewSet', api_models.CameraViewSet)
router.register('LabelViewSet', api_models.LabelViewSet)

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
    path('rest/', include(router.urls)),
    path('get_cameras/', api_methods.get_cameras)
]
