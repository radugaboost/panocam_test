from panocam_app.db.models import DetectionModel
from typing import Optional
import numpy as np
from panocam_app.detection.rknn_model import Rknn_yolov5s
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


class ModelPoolManager:

    def __init__(self, TPEs: int, model: DetectionModel) -> None:
        self._TPEs = TPEs
        self._queue = Queue()
        self._models = [Rknn_yolov5s(model.file_path, num) for num in range(TPEs)]
        self._pool = ThreadPoolExecutor(max_workers=TPEs)
        self._counter = 0

    def put(self, frame: np.ndarray) -> None:
        if self._counter > len(self._models):
            self._counter = 0

        self._queue.put(
            self._pool.submit(
                self._models[self._counter % self._TPEs].detect, frame
            )
        )

        self._counter += 1

    def get(self) -> Optional[np.ndarray]:
        if self._queue.empty():
            return None

        future = self._queue.get()
        return future.result()
