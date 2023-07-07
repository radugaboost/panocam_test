from django.urls import path
from . import views

urlpatterns = [
    path('camera_stream/<int:camera_id>/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
]