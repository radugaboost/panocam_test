from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer, ListField, IntegerField

from panocam_app.db.models import (
    Configuration, Camera,
    Label, VideoRecord
)
from panocam_app.db.models.detection_area import DetectionArea


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ConfigurationSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Configuration
        fields = '__all__'


class CameraSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'


class LabelSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'


class VideoRecordSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = VideoRecord
        fields = '__all__'


class DetectionAreaSerializer(HyperlinkedModelSerializer):
    points = ListField(child=ListField(child=IntegerField()))

    class Meta:
        model = DetectionArea
        fields = '__all__'
