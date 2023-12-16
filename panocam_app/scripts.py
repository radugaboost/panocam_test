from .models import Camera
from panocam_app.streaming.camera import ThreadedCamera

THREADED_CAMERAS = dict()


def get_available_cameras() -> list:
    return Camera.objects.all()


def start_camera(camera_id: int) -> None:
    camera = ThreadedCamera(camera_id)
    started = camera.start_video()
    if started:
        THREADED_CAMERAS[camera_id] = camera


def start_all_cameras() -> None:
    cameras = Camera.objects.all()
    for item in cameras:
        if item.id not in THREADED_CAMERAS.keys():
            start_camera(item.id)
