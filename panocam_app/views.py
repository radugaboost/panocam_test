from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from datetime import datetime
# from pixellib.instance import instance_segmentation

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


@gzip.gzip_page
def camera(request):
    cascade_path = './panocam_app/filters/haarcascade_frontalface_default.xml'
    def generate():
        clf = cv2.CascadeClassifier(cascade_path)
        capture = cv2.VideoCapture(0)
        
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # ширина
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # высота
        capture.set(cv2.CAP_PROP_BRIGHTNESS, 10)  # яркость
        capture.set(cv2.CAP_PROP_HUE, 10) # оттенок
        capture.set(cv2.CAP_PROP_CONTRAST, 19) # контрастность
        capture.set(cv2.CAP_PROP_SATURATION, 50) # насыщенность
        capture.set(cv2.CAP_PROP_FPS, 10) # частота кадров

        while True:
            _, frame = capture.read()
            
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
            
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

@gzip.gzip_page
def camera_stream(request):
    return render(request, 'camera.html')