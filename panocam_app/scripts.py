from .models import Camera
import cv2
from time import time, sleep
from datetime import datetime
from threading import Thread

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
            raise Exception(f"Не удалось открыть камеру с ip {camera.ip}")
        
        sleep(0.5)  # Пауза перед повторной попыткой
        capture = cv2.VideoCapture(int(camera.ip))


    settings = camera.image_config
    resolution = settings.resolution.split('x')
        
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(resolution[0]))  # ширина
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(resolution[1]))  # высота
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
        self.capture = create_capture(self.src)
        self.start_video()
    
    def start_recording(self):
        self.out = cv2.VideoWriter(
            f'./panocam_app/static/videos/{datetime.now()}.mp4',
            cv2.VideoWriter_fourcc(*'mp4v'),
            20.0,
            (640, 480)
        )
        self.recording_thread = Thread(target=self.recording)
        self.recording_thread.start()
    
    def recording(self):
        frame = self.frame
        while self.detect:
            if frame is self.frame:
                continue
            frame = self.frame
            self.out.write(frame)
        self.out.release()

    def start_video(self):
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
                
                for (x, y, width, height) in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

                # Получаем текущую дату и время
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Наложение текста с датой на кадр
                cv2.putText(frame, current_date, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                self.frame = frame

        self.capture.release()

    def show_frame(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg
    
    def restart(self):
        self.stop = True
        self.start_video()

def start_all_cameras():
    cameras = Camera.objects.all()
    for item in cameras:
        if item.id not in THREADED_CAMERAS.keys():
            thread = ThreadedCamera(item.id)
            THREADED_CAMERAS[item.id] = thread
