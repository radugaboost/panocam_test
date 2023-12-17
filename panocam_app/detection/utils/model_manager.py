from panocam_app.db.models import DetectionModel
import numpy as np
from panocam_app.detection.detection import Rknn_yolov5s

class ModelManager:
    models: list = []

    @classmethod
    def update_models(cls) -> None:
        cls.models = [Rknn_yolov5s(model.file_path) for model in DetectionModel.objects.filter(active=True)]

    @classmethod
    def process_models(cls, frame: np.ndarray) -> np.ndarray:
        if not cls.models and DetectionModel.objects.filter(active=True):
            cls.update_models()

        result_frame = frame
        for model in cls.models:
            result_frame = model.detect(result_frame)

        return result_frame