from django.urls import include, path
from rest_framework import routers

from panocam_app.recording.views import video_api
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

video_records_urls = [
    path('videos/', video_api.video_list, name='video_list'),
    path('videos/<int:video_id>/', video_api.video_page, name='video_page'),
    path('get_videos/', video_api.get_video_records, name='get_videos'),
    path('get_video_data/<int:video_id>/', video_api.get_video_data, name='get_video_data'),
    path('get_video_file/<int:video_id>/', video_api.get_video_file, name='get_video_file'),
    path('drop_video_record/<int:video_id>/', video_api.drop_video_record, name='drop_video_record'),
    path('drop_video_records/', video_api.drop_video_records, name='drop_video_records'),
]

urlpatterns.extend(stream_urls)
urlpatterns.extend(area_urls)
urlpatterns.extend(model_urls)
urlpatterns.extend(video_records_urls)
