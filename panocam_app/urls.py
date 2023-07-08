from django.urls import include, path
from rest_framework import routers
from . import views, api

router = routers.DefaultRouter()
router.register('ConfigurationViewSet', api.ConfigurationViewSet)
router.register('CameraViewSet', api.CameraViewSet)
router.register('LabelViewSet', api.LabelViewSet)

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
    path('rest/', include(router.urls)),
]
