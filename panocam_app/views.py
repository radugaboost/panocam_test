from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
from datetime import datetime
from . import models
from time import time, sleep
# from pixellib.instance import instance_segmentation

stop_streaming = False

def get_available_cameras():
    available_cameras = []

    for index in range(10):
        try:
            capture = cv2.VideoCapture(index)
            if capture.isOpened():
                available_cameras.append(index)
            capture.release()
        except:
            continue

    return available_cameras

def create_capture(camera_id: int, timeout=2):
    camera = models.Camera.objects.get(id=camera_id)
    start_time = time()
    capture = cv2.VideoCapture(int(camera.ip))

    while not capture.isOpened():
        elapsed_time = time() - start_time
        if elapsed_time > timeout:
            raise Exception(f"Не удалось открыть камеру с ip {camera.ip}")
        
        sleep(0.05)  # Пауза перед повторной попыткой
        capture = cv2.VideoCapture(int(camera.ip))


    settings = camera.image_config
        
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)  # ширина
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)  # высота
    capture.set(cv2.CAP_PROP_BRIGHTNESS, settings.brightness)  # яркость
    capture.set(cv2.CAP_PROP_HUE, settings.hue) # оттенок
    capture.set(cv2.CAP_PROP_CONTRAST, settings.contrast) # контрастность
    capture.set(cv2.CAP_PROP_SATURATION, settings.saturation) # насыщенность
    capture.set(cv2.CAP_PROP_FPS, settings.fps_rate) # частота кадров
    
    return capture
    


@gzip.gzip_page
def camera(request, camera_id: int):
    cascade_path = './panocam_app/filters/haarcascade_frontalface_default.xml'
    def generate():
        clf = cv2.CascadeClassifier(cascade_path)
        capture = create_capture(
            camera_id=camera_id
        )

        while True:
            success, frame = capture.read()
            
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
                
                for (x, y, width, height) in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                
                
                
                # Получаем текущую дату и время
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Наложение текста с датой на кадр
                cv2.putText(frame, current_date, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, 'Kirill dirka', (450, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

@gzip.gzip_page
def camera_stream(request):
    return render(request, 'camera.html')