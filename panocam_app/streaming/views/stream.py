from django.shortcuts import render
from django.http import (
    StreamingHttpResponse, HttpResponseNotFound,
    HttpResponse, HttpRequest
)
from django.views.decorators.gzip import gzip_page
from panocam_app.scripts import THREADED_CAMERAS
from .utils import generate


@gzip_page
def camera(
        request: HttpRequest, camera_id: int, area_id: int = None
    ) -> StreamingHttpResponse or HttpResponseNotFound:
    print(THREADED_CAMERAS)
    frame_type = request.GET.get('frame_type', '')
    camera = THREADED_CAMERAS.get(camera_id)

    if camera:
        area = camera.areas.get(area_id)
        return StreamingHttpResponse(
            generate(camera, area, frame_type),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    return HttpResponseNotFound()


def check_camera(
        request: HttpRequest, camera_id: int
    ) -> HttpResponse or HttpResponseNotFound:
    if camera_id in THREADED_CAMERAS.keys():
        return HttpResponse()
    return HttpResponseNotFound()


@gzip_page
def camera_stream(request: HttpRequest) -> render:
    return render(request, 'camera.html')
