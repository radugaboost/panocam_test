from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from .models import Camera
from .scripts import THREADED_CAMERAS
import os

def video_list(request):
    video_dir = './panocam_app/static/videos'
    video_files = os.listdir(video_dir)
    video_list = []

    for filename in video_files:
        if filename.endswith('.mp4'):
            video_path = os.path.join('/static/videos/', filename)
            video_list.append(video_path)

    context = {
        'video_list': video_list
    }

    return render(request, 'video.html', context)


def get_available_cameras():
    return Camera.objects.all()

def generate(camera_id: int):
    if camera_id in THREADED_CAMERAS.keys():
        capture = THREADED_CAMERAS[camera_id]
        while True:
            jpeg = capture.show_frame()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@gzip.gzip_page
def camera(request, camera_id: int):
    return StreamingHttpResponse(
        generate(camera_id),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@gzip.gzip_page
def camera_stream(request):
    return render(request, 'camera.html', {'cameras': get_available_cameras()})
