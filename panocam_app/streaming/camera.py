from panocam_app.streaming.utils.capture import create_capture
from panocam_app.models import DetectionModel
from threading import Thread
import numpy as np
from queue import Queue
from panocam_app.image_processing.reformat_frame import warp_image
from panocam_app.recording.recording import SaveVideo
from panocam_app.streaming.utils.check_day import day_has_changed
from django.utils import timezone
from panocam_app.detection.utils.pool_manager import ModelPoolManager


class ThreadedCamera(object):
    def __init__(self, camera_id: int = 0) -> None:
        self.__frame = None
        self.id = camera_id
        self.areas = dict()
        self.queue = Queue()
        self.previous_day = timezone.now().day

    def start_video(self) -> bool:
        self.capture = create_capture(self.id)

        if not self.capture:
            return False

        self.thread = Thread(target=self.update)
        self.thread.daemon = True
        self.stop = False
        self.queue = Queue()
        self.thread.start()
        self.record = SaveVideo(self.queue, self.id)

        Thread(target=self.record.start_recording).start()

        return True

    def update(self) -> None:
        # pool = ModelPoolManager(TPEs=3, model=DetectionModel.objects.get(id=1))
        while not self.stop:
            success, frame = self.capture.read()

            if success:
                warped_frame = warp_image(frame)
                self.__frame = warped_frame

                # pool.put(warped_frame)
                # processed_frame = pool.get()

                # if frame is None:
                #     self.__frame = warped_frame
                # else:
                #     self.__frame = processed_frame

                if self.queue:
                    self.queue.put(self.__frame)

            if day_has_changed(self.previous_day):
                self.restart()

    def show_frame(self) -> np.ndarray:
        return self.__frame

    def restart(self) -> None:
        if self.record:
            self.record.stop_recording()

        self.stop = True
        self.capture.release()
        return self.start_video()
