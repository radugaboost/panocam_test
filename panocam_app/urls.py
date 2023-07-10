from django.urls import include, path
from rest_framework import routers
from . import views, api_models

router = routers.DefaultRouter()
router.register(r'User', api_models.UserViewSet)
router.register(r'Configuration', api_models.ConfigurationViewSet)
router.register(r'Camera', api_models.CameraViewSet)
router.register(r'Label', api_models.LabelViewSet)

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
    path('rest/', include(router.urls)),
    path('video_list/', views.video_list, name='video_list'),
    path('check_camera/<int:camera_id>/', views.check_camera, name='check_camera'),
]
