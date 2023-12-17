from .utils.capture import create_capture
from threading import Thread
import numpy as np
from queue import Queue
from panocam_app.image_processing.reformat.warp import warp_image
from panocam_app.recording.recording import SaveVideo
from .utils.check_day import day_has_changed
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

    def add_area(self, points: list, shape: list) -> int:
        height, width = shape
        init_height, init_width = self.__frame.shape[:2]
        x_modifier, y_modifier = init_width / width, init_height / height

        top, height, left, width = 0, 0, 0, 0
        modified_points = list()
        for point in points:
            x, y = int(point['x'] * x_modifier), int(point['y'] * y_modifier)
            modified_points.append((x, y))
            if not top:
                top, height = y, y
                left, width = x, x
                continue

            top, height = min(top, y), max(height, y)
            left, width = min(left, x), max(width, x)

        area_id = len(self.areas) + 1
        self.areas[area_id] = [(top, left, width, height), modified_points]
        return area_id
