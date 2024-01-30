from typing import List, Any

import cv2
import numpy as np

from .utils.capture import create_capture
from threading import Thread
from numpy import ndarray
from queue import Queue
from panocam_app.image_processing.reformat.warp import warp_image
from panocam_app.recording.utils.recording import SaveVideo
from .utils.check_day import day_has_changed
from django.utils import timezone
from panocam_app.detection.utils.pool_manager import ModelPoolManager
from panocam_app.db.models import DetectionModel, DetectionArea


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
        pool = ModelPoolManager(TPEs=3, model=DetectionModel.objects.all()[0])
        while not self.stop:
            success, frame = self.capture.read()

            if success:
                pool.put(frame)
                detection_frame, detected_boxes, detected_classes = pool.get()
                self.__frame = self.add_areas_on_frame(frame, detected_boxes, detected_classes)

                self.__warped_frame = warp_image(frame)

                if detection_frame is not None:
                    self.__detection_frame = detection_frame

                if self.queue:
                    self.queue.put(self.__frame)

            if day_has_changed(self.previous_day):
                self.restart()

    def add_areas_on_frame(self, frame, detected_boxes, detected_classes):
        areas = DetectionArea.objects.filter(camera=self.id)

        frame_with_areas = frame.copy()

        for area in areas:
            area_points = area.points
            shape = map(int, area.shape.split('x'))
            modified_points = self.modify_points(area_points, shape, frame.shape[:2])

            poly_area = np.array(modified_points, dtype=np.int32)

            if detected_classes is not None and self.check_collision(detected_boxes, poly_area, detected_classes, area.label):
                mask = np.zeros_like(frame_with_areas)

                cv2.fillPoly(mask, [poly_area], color=(0, 0, 255))

                frame_with_areas = cv2.addWeighted(frame_with_areas, 1, mask, 0.5, 0)
            else:
                cv2.polylines(frame_with_areas, [poly_area], isClosed=True, color=(0, 255, 0), thickness=2)

            label_text = f"ID: {area.id}, Label: {area.label}"
            cv2.putText(frame_with_areas, label_text, tuple(modified_points[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                        (255, 255, 255), 1, cv2.LINE_AA)

        return frame_with_areas

    @staticmethod
    def check_collision(detected_boxes, area_points, detected_classes, label):
        for box, model_class in zip(detected_boxes, detected_classes):
            x_axis, y_axis, width, height = box
            if (cv2.pointPolygonTest(area_points, (x_axis + width / 2, y_axis + height / 2), False) >= 0
                    and model_class == label):
                return True
        return False

    @staticmethod
    def modify_points(points, shape, frame_shape):
        height, width = shape
        init_height, init_width = frame_shape
        x_modifier, y_modifier = init_width / width, init_height / height

        modified_points = []

        for point in points:
            x_axis, y_axis = int(point[0] * x_modifier), int(point[1] * y_modifier)
            modified_points.append((x_axis, y_axis))

        return modified_points

    def show_frame(self, frame_type: str) -> ndarray | list[Any]:
        if frame_type == 'warped':
            return self.__warped_frame

        elif frame_type == 'detection':
            return self.__detection_frame

        return self.__frame

    def restart(self) -> bool:
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
