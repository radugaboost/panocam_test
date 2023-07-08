from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Configuration, Camera, Label


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
