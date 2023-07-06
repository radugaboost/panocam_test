from django.urls import path
from . import views

urlpatterns = [
    path('cameraa/', views.camera, name='camera_stream'),
    path('camera/', views.camera_stream, name='camera'),
]