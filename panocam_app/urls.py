from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('ConfigurationViewSet', views.ConfigurationViewSet)
router.register('CameraViewSet', views.CameraViewSet)
router.register('LabelViewSet', views.LabelViewSet)

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
    path('rest/', include(router.urls)),
]
