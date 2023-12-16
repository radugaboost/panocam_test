from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from panocam_app.serializers import (
    ConfigurationSerializer, CameraSerializer, LabelSerializer,
    UserSerializer, VideoRecordSerializer
)
from panocam_app.models import (
    Configuration, Camera,
    Label, VideoRecord
)

def query_from_request(request, cls_serializer=None) -> dict:
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET


class Permission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in {'GET', 'HEAD', 'OPTIONS', 'PATCH'}:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in {'POST', 'PUT', 'DELETE'}:
            return bool(request.user and request.user.is_superuser)
        return False


def create_viewset(cls_model, serializer, permission, order_field='id'):
    class_name = '{0}ViewSet'.format(cls_model.__name__)
    doc = 'API endpoint that allows users to be viewed or edited for {0}'.format(cls_model.__name__)
    return type(
        class_name,
        (viewsets.ModelViewSet,),
        {
            '__doc__': doc,
            'serializer_class': serializer,
            'queryset': cls_model.objects.all().order_by(order_field),
            'permission_classes': [permission],
            'get_queryset': lambda queryset_self, *args, **kwargs: cls_model.objects.filter(
                **query_from_request(queryset_self.request, serializer),
            ).order_by(order_field),
        },
    )


ConfigurationViewSet = create_viewset(Configuration, ConfigurationSerializer, Permission)
CameraViewSet = create_viewset(Camera, CameraSerializer, Permission)
LabelViewSet = create_viewset(Label, LabelSerializer, Permission)
UserViewSet = create_viewset(User, UserSerializer, Permission)
VideoRecordSet = create_viewset(VideoRecord, VideoRecordSerializer, Permission)
