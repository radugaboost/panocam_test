from django.utils import timezone
from .models import Camera, DetectionModel
import cv2
from time import time, sleep
from threading import Thread
from queue import Queue
from panocam_app.detection import Rknn_yolov5s
from panocam_app.reformat_frame import warp_image
from .recording import SaveVideo

THREADED_CAMERAS = dict()


def get_available_cameras():
    return Camera.objects.all()


def create_capture(camera_id: int, timeout=1):
    camera = Camera.objects.get(id=camera_id)
    start_time = time()
    capture = cv2.VideoCapture(camera.ip)

    while not capture.isOpened():
        elapsed_time = time() - start_time
        if elapsed_time > timeout:
            print(f"Не удалось открыть камеру с ip {camera.ip}")
            return False

        sleep(0.5)  # Пауза перед повторной попыткой
        capture = cv2.VideoCapture(camera.ip)

    return capture


class ModelManager:
    models = []

    @classmethod
    def update_models(cls):
        cls.models = [Rknn_yolov5s(model.file_path) for model in DetectionModel.objects.filter(active=True)]

    @classmethod
    def process_models(cls, frame):
        if not cls.models and not DetectionModel.objects.filter(active=True):
            cls.update_models()

        result_frame = frame
        for model in cls.models:
            result_frame = model.detect(result_frame)
        return result_frame


class ThreadedCamera(object):
    def __init__(self, camera_id=0):
        self.__frame = None
        self.camera_id = camera_id
        self.areas = dict()
        self.queue = None
        self.previous_day = timezone.now().day
        self.start_video()
        self.record = None

    def day_has_changed(self):
        current_day = timezone.now().day
        if current_day != self.previous_day:
            self.previous_day = current_day
            return True
        return False

    def start_video(self):
        self.capture = create_capture(self.camera_id)
        if not self.capture:
            if self.camera_id in THREADED_CAMERAS.keys():
                del THREADED_CAMERAS[self.camera_id]
            return False
        self.thread = Thread(target=self.update)
        self.thread.daemon = True
        self.stop = False
        self.thread.start()
        self.queue = Queue()
        self.record = SaveVideo(self.queue, self.camera_id)
        Thread(target=self.record.start_recording).start()

    def update(self):
        while not self.stop:
            success, frame = self.capture.read()
            warped_frame = warp_image(frame)
            flipped_frame = (cv2.flip(warped_frame, 1))  # зеркалит кадр
            # flipped_frame = (cv2.flip(frame, 1))

            if success:
                self.__frame = ModelManager.process_models(flipped_frame)

                if self.queue:
                    self.queue.put(self.__frame)
            if self.day_has_changed():
                self.restart()

    def show_frame(self):
        return self.__frame

    def restart(self):
        if self.record:
            self.record.stop_recording()
        self.stop = True
        self.capture.release()
        self.start_video()


def start_camera(camera_id: int):
    thread = ThreadedCamera(camera_id)
    if thread.capture:
        THREADED_CAMERAS[camera_id] = thread


def start_all_cameras():
    cameras = Camera.objects.all()
    for item in cameras:
        if item.id not in THREADED_CAMERAS.keys():
            start_camera(item.id)

    print(THREADED_CAMERAS)
