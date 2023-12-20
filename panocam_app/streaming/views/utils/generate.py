from panocam_app.streaming.camera import ThreadedCamera
from panocam_app.image_processing.select.area import select_area
from cv2 import imencode


def generate(
        camera: ThreadedCamera, area: list, frame_type: str
    ):
    while True:
        frame = camera.show_frame(frame_type)

        if area:
            frame = select_area(area, frame)

        _, jpeg = imencode('.jpg', frame)
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')