from panocam_app.db.models import DetectionModel
from typing import Optional
import numpy as np
# from panocam_app.detection.rknn_model import Rknn_yolov5s
from panocam_app.detection.simple_yolo_model import SimpleYolo
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


class ModelPoolManager:

    def __init__(self, TPEs: int, models: [DetectionModel]) -> None:
        self._TPEs = TPEs
        self._queue = Queue()
        self._models = [SimpleYolo(model.id, num) for num, model in enumerate(models) if num <= TPEs]
        self._pool = ThreadPoolExecutor(max_workers=TPEs)
        self._counter = 0

    def put(self, frame: np.ndarray) -> None:
        if len(self._models) < self._counter:
            self._counter += 1
        elif len(self._models) >= self._counter:
            self._counter = 0

        if len(self._models) != 0:
            self._queue.put(
                self._pool.submit(
                    self._models[self._counter % self._TPEs].detect, frame
                )
            )

    def get(self) -> Optional[np.ndarray]:
        if self._queue.empty():
            return None

        future = self._queue.get()
        return future.result()
