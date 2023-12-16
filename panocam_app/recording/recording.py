from threading import Thread
from django.utils import timezone
import cv2

from panocam_app.models import Camera, VideoRecord

SAVING_PATH = './panocam_app/storage/videos/{0}.avi'


class SaveVideo:
    def __init__(self, queue, camera_id):
        self.queue = queue
        self.record = None
        self.stop = not Camera.objects.get(id=camera_id).is_recording

    def start_recording(self):
        if not self.stop:
            name = str(timezone.localtime(timezone.now(), timezone=timezone.get_current_timezone()))
            saving_path = SAVING_PATH.format(name)
            self.record = VideoRecord.objects.create(
                name=name,
                start=name,
                saving_path=saving_path
            )

            self.out = cv2.VideoWriter(
                # f'./panocam_app_copy/static/videos/{timezone.now()}.mp4',
                saving_path,
                # cv2.VideoWriter_fourcc(*"avc1"),
                cv2.VideoWriter_fourcc(*"XVID"),
                20.0,
                (640, 480)
            )
            Thread(target=self.recording).start()

    def recording(self):
        while not self.stop:
            if not self.queue.empty():
                frame = self.queue.get()
                self.out.write(frame)
        self.record.end = timezone.now()
        self.record.save(update_fields=['end'])

    def stop_recording(self):
        self.stop = True
