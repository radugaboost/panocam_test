from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Camera
from .serializers import CameraSerializer


@api_view(['GET'])
def get_cameras(request):
    cameras = Camera.objects.all()
    print(cameras)
    return Response(CameraSerializer(cameras, many=True, context={'request': request}).data)
