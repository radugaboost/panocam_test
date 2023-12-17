from json import loads
from django.http import (
    JsonResponse, HttpRequest
)
from panocam_app.streaming.camera import ThreadedCamera
from panocam_app.scripts import THREADED_CAMERAS

def add_area(request: HttpRequest, camera_id: int) -> JsonResponse:
    camera: ThreadedCamera = THREADED_CAMERAS.get(camera_id)
    if camera:
        data = request.body.decode('utf-8')
        json_data = loads(data)

        area_id = camera.add_area(
            json_data.get('points'), json_data.get('shape')
        )

        return JsonResponse(data={'area_id': area_id}, status=201)

    return JsonResponse(data={'message': 'Not found'},status=404)