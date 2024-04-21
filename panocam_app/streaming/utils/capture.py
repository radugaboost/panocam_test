from panocam_app.db.models import Camera
from typing import Optional
from time import time, sleep
from cv2 import VideoCapture, CAP_FFMPEG


def create_capture(camera_id: int, timeout: int = 1) -> Optional[VideoCapture]:
    camera = Camera.objects.get(id=camera_id)
    start_time = time()
    capture = VideoCapture(int(camera.ip), CAP_FFMPEG)
    print(capture, capture.isOpened())
    while not capture.isOpened():
        elapsed_time = time() - start_time
        print(elapsed_time, timeout)
        if elapsed_time > timeout:
            print(f"Не удалось открыть камеру с ip {camera.ip}")
            return None

        sleep(timeout // 2)
        capture = VideoCapture(int(camera.ip))

    return capture
