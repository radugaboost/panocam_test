from django.urls import include, path
from rest_framework import routers
from panocam_app.streaming.views import area, stream
from panocam_app.api import api_models
from panocam_app.models.views import cruds as model

router = routers.DefaultRouter()
router.register(r'User', api_models.UserViewSet)
router.register(r'Configuration', api_models.ConfigurationViewSet)
router.register(r'Camera', api_models.CameraViewSet)
router.register(r'Label', api_models.LabelViewSet)
router.register(r'VideoRecord', api_models.VideoRecordSet)


urlpatterns = [
    path('rest/', include(router.urls)),
]


stream_urls = [
    path('camera_stream/<int:camera_id>/', stream.camera, name='camera_stream'),
    path('camera_stream/<int:camera_id>/<int:area_id>', stream.camera, name='camera_stream'),
    path('camera/', stream.camera_stream, name='camera'),
]


area_urls = [
    path('add_area/<int:camera_id>/', area.add_area, name='add_area'),
]


model_urls = [
    path('load_model/', model.upload_page, name='upload_file'),
    path('save_model/', model.upload_file, name='save_model'),
    path('change_model_status/<int:model_id>/', model.change_model_status, name='change_model_status'),
    path('delete_model/<int:model_id>/', model.delete_model, name='delete_model'),
]


urlpatterns.extend(stream_urls)
urlpatterns.extend(area_urls)
urlpatterns.extend(model_urls)
