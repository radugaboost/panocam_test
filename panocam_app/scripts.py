from panocam_app.db.models import Camera
from panocam_app.streaming import ThreadedCamera


THREADED_CAMERAS = dict()


def start_camera(camera_id: int) -> None:
    camera = ThreadedCamera(camera_id)
    started = camera.start_video()
    if started:
        THREADED_CAMERAS[camera_id] = camera


def start_all_cameras() -> None:
    cameras = Camera.objects.all()
    for camera in cameras:
        if camera.id not in THREADED_CAMERAS.keys():
            start_camera(camera.id)
