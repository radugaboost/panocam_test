from .models import Camera
import cv2
from time import time, sleep
from datetime import datetime
from threading import Thread
from queue import Queue

THREADED_CAMERAS = dict()

def get_available_cameras():
    return Camera.objects.all()

def create_capture(camera_id: int, timeout=2):
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
        
    capture.set(3, int(resolution[0]))  # ширина
    capture.set(4, int(resolution[1]))  # высота
    capture.set(cv2.CAP_PROP_BRIGHTNESS, settings.brightness)  # яркость
    capture.set(cv2.CAP_PROP_HUE, settings.hue) # оттенок
    capture.set(cv2.CAP_PROP_CONTRAST, settings.contrast) # контрастность
    capture.set(cv2.CAP_PROP_SATURATION, settings.saturation) # насыщенность
    capture.set(cv2.CAP_PROP_FPS, settings.frame_rate) # частота кадров
    
    return capture

class ThreadedCamera(object):
    def __init__(self, src=0):
        self.frame = None
        self.src = src
        self.detect = False
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
    
    def recording(self):
        while self.detect:
            if not self.queue.empty():
                frame = self.queue.get()
                self.out.write(frame)

    def start_video(self):
        self.capture = create_capture(self.src)
        if not self.capture:
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
        
            frame = cv2.flip(frame, 1)  # зеркалит кадр
            
            if success:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


                faces = clf.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=10,
                    minSize=(50,50),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                if len(faces) > 0 and not self.detect:
                    self.detect = True
                    self.start_recording()
                if len(faces) == 0 and self.detect:
                    self.detect = False
                    self.queue = None
                    self.out.release()
                
                for (x, y, width, height) in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

                # Получаем текущую дату и время
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Наложение текста с датой на кадр
                cv2.putText(frame, current_date, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                self.frame = frame
                if self.queue:
                    self.queue.put(self.frame)

    def show_frame(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg
    
    def restart(self):
        self.stop = True
        self.capture.release()
        self.start_video()

def start_all_cameras():
    cameras = Camera.objects.all()
    for item in cameras:
        if item.id not in THREADED_CAMERAS.keys():
            thread = ThreadedCamera(item.id)
            if thread.capture:
                THREADED_CAMERAS[item.id] = thread
    print(THREADED_CAMERAS)