from .models import Camera, DetectionModel
import cv2
from time import time, sleep
from datetime import datetime
from threading import Thread
from queue import Queue
from panocam_app.detection import Rknn_yolov5s
from panocam_app.reformat_frame import warp_image

THREADED_CAMERAS = dict()


def get_available_cameras():
    return Camera.objects.all()


def create_capture(camera_id: int, timeout=1):
    camera = Camera.objects.get(id=camera_id)
    start_time = time()
    capture = cv2.VideoCapture(int(camera.ip))

    while not capture.isOpened():
        elapsed_time = time() - start_time
        if elapsed_time > timeout:
            print(f"Не удалось открыть камеру с ip {camera.ip}")
            return False

        sleep(0.5)  # Пауза перед повторной попыткой
        capture = cv2.VideoCapture(int(camera.ip))

    return capture


class ModelManager:
    models = []

    @classmethod
    def update_models(cls):
        cls.models = [Rknn_yolov5s(model.file_path) for model in DetectionModel.objects.filter(active=True)]

    @classmethod
    def process_models(cls, frame):
        if not cls.models:
            cls.update_models()

        result_frame = frame
        for model in cls.models:
            result_frame = model.detect(result_frame)
        return result_frame


class ThreadedCamera(object):
    def __init__(self, src=0):
        self.__frame = None
        self.src = src
        self.queue = None
        self.start_video()

    def start_recording(self):
        self.out = cv2.VideoWriter(
            f'./panocam_app/static/videos/{datetime.now()}.mp4',
            cv2.VideoWriter_fourcc(*"avc1"),
            20.0,
            (640, 480)
        )
        self.recording_thread = Thread(target=self.recording)
        self.queue = Queue()
        self.recording_thread.start()

    def recording(self): # TODO
        print('Starting detect recording')
        prev_frame = None
        while self.detect:
            if not self.queue.empty():
                frame = self.queue.get()
                self.out.write(frame)
        print('Recording finished')

    def start_video(self):
        self.capture = create_capture(self.src)
        if not self.capture:
            if self.src in THREADED_CAMERAS.keys():
                del THREADED_CAMERAS[self.src]
            return False
        self.thread = Thread(target=self.update)
        self.thread.daemon = True
        self.stop = False
        self.thread.start()

    def update(self):
        while not self.stop:
            success, frame = self.capture.read()
            warped_frame = warp_image(frame)
            flipped_frame = (cv2.flip(warped_frame, 1))  # зеркалит кадр

            if success:
                self.__frame = ModelManager.process_models(flipped_frame)

                if self.queue:
                    self.queue.put(self.__frame)

    def show_frame(self):
        return self.__frame

    def restart(self):
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
