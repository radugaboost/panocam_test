from django.urls import include, path
from rest_framework import routers
from . import views, api_models

router = routers.DefaultRouter()
router.register('UserViewSet', api_models.UserViewSet, basename='user')
router.register('ConfigurationViewSet', api_models.ConfigurationViewSet, basename='configuration')
router.register('CameraViewSet', api_models.CameraViewSet, basename='camera')
router.register('LabelViewSet', api_models.LabelViewSet, basename='label')

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
    path('rest/', include(router.urls)),
]
