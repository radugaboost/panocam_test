from .models import Camera
import cv2
from time import time, sleep
from datetime import datetime
from threading import Thread
from queue import Queue
import numpy as np

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


    settings = camera.image_config
    resolution = settings.resolution.split('x')
        
    # capture.set(3, int(resolution[0]))  # ширина
    # capture.set(4, int(resolution[1]))  # высота
    # capture.set(cv2.CAP_PROP_BRIGHTNESS, settings.brightness)  # яркость
    # capture.set(cv2.CAP_PROP_HUE, settings.hue) # оттенок
    # capture.set(cv2.CAP_PROP_CONTRAST, settings.contrast) # контрастность
    # capture.set(cv2.CAP_PROP_SATURATION, settings.saturation) # насыщенность
    # capture.set(cv2.CAP_PROP_FPS, settings.frame_rate) # частота кадров
    
    return capture

class ThreadedCamera(object):
    def __init__(self, src=0):
        self.frame = None
        self.src = src
        self.detect = False
        self.queue = None
        self.detected_objects = tuple()
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
    
    def recording(self):
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
        cascade_path = './panocam_app/filters/haarcascade_frontalface_default.xml'
        clf = cv2.CascadeClassifier(cascade_path)
        while not self.stop:
            success, frame = self.capture.read()
            flipped_frame = cv2.flip(frame, 1)  # зеркалит кадр
            preprocessed_frame = cv2.resize(flipped_frame, (1280, 720))

            if success:
                gray = cv2.cvtColor(preprocessed_frame, cv2.COLOR_BGR2GRAY)
                faces = clf.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=10,
                    minSize=(50,50),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                self.frame = ThreadedCamera.frame_process(preprocessed_frame, faces, (160, 160))

                if self.queue:
                    self.queue.put(self.frame)

    @staticmethod
    def frame_process(frame: np, detected_objects: list, object_image_size: tuple):
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        combined_height = frame_height + object_image_size[0]
        combined_frame = np.zeros((combined_height, frame_width, 3), dtype=np.uint8)

        if len(detected_objects) > 0:
            resized_objects = []

            clone_frame = frame.copy()
            for (x, y, width, height) in detected_objects:
                object_image = clone_frame[y:y + height, x:x + width]
                resized_object = cv2.resize(object_image, (object_image_size))
                resized_objects.append(resized_object)
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

            current_x = 0 # начальное положение для вставки изображения
            for object_image in resized_objects:
                object_width = object_image.shape[1]
                if current_x + object_width > frame_width:
                    frame_height += object_image.shape[1]
                    combined_height += object_image.shape[1]
                    current_x = 0
                combined_frame[frame_height:combined_height, current_x:current_x + object_width] = object_image
                current_x += object_width # сдвигаем текущее положение

        combined_frame[:frame_height, :frame_width] = frame
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # подставляем текущее время
        cv2.putText(combined_frame, current_date, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return combined_frame

    def show_frame(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg
    
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