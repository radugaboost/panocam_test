from django.utils import timezone
from .models import Camera, DetectionModel
from typing import Optional
import cv2
from time import time, sleep
from threading import Thread
from datetime import datetime
import numpy as np
from queue import Queue
from panocam_app.detection import Rknn_yolov5s
from panocam_app.reformat_frame import warp_image
from .recording import SaveVideo
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

THREADED_CAMERAS = dict()


def get_available_cameras() -> list:
    return Camera.objects.all()


def create_capture(camera_id: int, timeout: int = 1) -> Optional[cv2.VideoCapture]:
    camera = Camera.objects.get(id=camera_id)
    start_time = time()
    capture = cv2.VideoCapture(camera.ip)

    while not capture.isOpened():
        elapsed_time = time() - start_time
        if elapsed_time > timeout:
            print(f"Не удалось открыть камеру с ip {camera.ip}")
            return None

        sleep(timeout // 2)
        capture = cv2.VideoCapture(camera.ip)

    return capture


class ModelPoolManager:

    def __init__(self, TPEs: int, model: DetectionModel) -> None:
        self._TPEs = TPEs
        self._queue = Queue()
        self._models = [Rknn_yolov5s(model.file_path, num) for num in range(TPEs)]
        self._pool = ThreadPoolExecutor(max_workers=TPEs)
        self._counter = 0

    def put(self, frame: np.ndarray) -> None:
        self._queue.put(
            self._pool.submit(
                self._models[self._counter % self._TPEs].detect, frame
            )
        )
        self._counter += 1

    def get(self) -> Optional[np.ndarray]:
        if self._queue.empty():
            return None

        future = self._queue.get()
        return future.result()



class ModelManager:
    models: list = []

    @classmethod
    def update_models(cls) -> None:
        cls.models = [Rknn_yolov5s(model.file_path) for model in DetectionModel.objects.filter(active=True)]

    @classmethod
    def process_models(cls, frame: np.ndarray) -> np.ndarray:
        if not cls.models and DetectionModel.objects.filter(active=True):
            cls.update_models()

        result_frame = frame
        for model in cls.models:
            result_frame = model.detect(result_frame)

        return result_frame


class ThreadedCamera(object):
    def __init__(self, camera_id: int = 0) -> None:
        self.__frame = None
        self.id = camera_id
        self.areas = dict()
        self.queue = Queue()
        self.previous_day = timezone.now().day

    def day_has_changed(self) -> bool:
        current_day = timezone.now().day
        if current_day != self.previous_day:
            self.previous_day = current_day
            return True
        return False

    def start_video(self) -> bool:
        self.capture = create_capture(self.camera_id)

        if not self.capture:
            return False

        self.thread = Thread(target=self.update)
        self.thread.daemon = True
        self.stop = False
        self.queue = Queue()
        self.thread.start()
        self.record = SaveVideo(self.queue, self.camera_id)

        Thread(target=self.record.start_recording).start()

        return True

    def update(self) -> None:
        pool = ModelPoolManager(TPEs=3, model=DetectionModel.objects.get(id=1))
        while not self.stop:
            success, frame = self.capture.read()

            if success:
                warped_frame = warp_image(frame)

                pool.put(warped_frame)
                processed_frame = pool.get()

                if frame is None:
                    self.__frame = warped_frame
                else:
                    self.__frame = processed_frame

                if self.queue:
                    self.queue.put(self.__frame)

            if self.day_has_changed():
                self.restart()

    def show_frame(self) -> np.ndarray:
        return self.__frame

    def restart(self) -> None:
        if self.record:
            self.record.stop_recording()

        self.stop = True
        self.capture.release()
        return self.start_video()


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
