from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip

@gzip.gzip_page
def camera(request):
    cascade_path = './panocam_app/filters/haarcascade_frontalface_default.xml'
    def generate():
        clf = cv2.CascadeClassifier(cascade_path)
        camera = cv2.VideoCapture(0)
        
        while True:
            _, frame = camera.read()
            
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
            
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


@gzip.gzip_page
def camera_stream(request):
    return render(request, 'camera.html')