from panocam_app.db.models import Camera
from typing import Optional
from time import time, sleep
import cv2


def create_capture(camera_id: int, timeout: int = 1) -> Optional[cv2.VideoCapture]:
    camera = Camera.objects.get(id=camera_id)
    start_time = time()
    capture = cv2.VideoCapture(int(camera.ip))

    while not capture.isOpened():
        elapsed_time = time() - start_time
        if elapsed_time > timeout:
            print(f"Не удалось открыть камеру с ip {camera.ip}")
            return None

        sleep(timeout // 2)
        capture = cv2.VideoCapture(int(camera.ip))

    return capture
