import cv2
import numpy as np
from rknnlite.api import RKNNLite
from typing import Optional


class Rknn_yolov5s:

    def __init__(
        self,
        rknn_model: str,
        npu_id: int = 0
    ) -> None:
        self.__rknn_model = Rknn_yolov5s.initRKNN(rknn_model, npu_id)
        self.__classes = (
            "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
            "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant",
            "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
            "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock",
            "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        )
        self.__obj_thresh = 0.65
        self.__nms_thresh = 0.45
        self.__image_size = (640, 640)
        self.__masks = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8]
        ]
        self.__anchors = [
            [10, 13], [16, 30], [33, 23],
            [30, 61], [62, 45], [59, 119],
            [116, 90], [156, 198], [373, 326]
        ]

    @staticmethod
    def initRKNN(rknnModel: str, npu_id: int) -> RKNNLite:
        rknn_lite = RKNNLite()
        ret = rknn_lite.load_rknn(rknnModel)

        if ret != 0:
            print("Load RKNN rknnModel failed")
            exit(ret)

        if npu_id == 0:
            ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)
        elif npu_id == 1:
            ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_1)
        elif npu_id == 2:
            ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_2)
        else:
            ret = rknn_lite.init_runtime()

        if ret != 0:
            print("Init runtime environment failed")
            exit(ret)

        print(rknnModel, "done")
        return rknn_lite

    def process(
        self, input: np.ndarray, mask: list, anchors: list
    ) -> tuple[
        Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]
    ]:
        anchors = [anchors[i] for i in mask]
        grid_h, grid_w = map(int, input.shape[0:2])

        box_confidence = input[..., 4]
        box_confidence = np.expand_dims(box_confidence, axis=-1)
        box_class_probs = input[..., 5:]
        box_xy = input[..., :2] * 2 - 0.5

        col = np.tile(np.arange(0, grid_w), grid_w).reshape(-1, grid_w)
        row = np.tile(np.arange(0, grid_h).reshape(-1, 1), grid_h)
        col = col.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        row = row.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        grid = np.concatenate((col, row), axis=-1)
        box_xy += grid
        box_xy *= int(self.__image_size[0] / grid_h)

        box_wh = pow(input[..., 2:4] * 2, 2)
        box_wh = box_wh * anchors

        return np.concatenate((box_xy, box_wh), axis=-1), box_confidence, box_class_probs

    def filter_boxes(
        self,
        boxes: np.ndarray,
        box_confidences: np.ndarray,
        box_class_probs: np.ndarray
    ) -> tuple[
        Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]
    ]:
        boxes = boxes.reshape(-1, 4)
        box_confidences = box_confidences.reshape(-1)
        box_class_probs = box_class_probs.reshape(-1, box_class_probs.shape[-1])

        _box_pos = np.where(box_confidences >= self.__obj_thresh)
        boxes = boxes[_box_pos]
        box_confidences = box_confidences[_box_pos]
        box_class_probs = box_class_probs[_box_pos]

        class_max_score = np.max(box_class_probs, axis=-1)
        classes = np.argmax(box_class_probs, axis=-1)
        _class_pos = np.where(class_max_score >= self.__obj_thresh)

        return boxes[_class_pos], classes[_class_pos], (class_max_score * box_confidences)[_class_pos]

    def nms_boxes(self, boxes: np.ndarray, scores: np.ndarray) -> np.ndarray:
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
        h = boxes[:, 3] - boxes[:, 1]

        areas = w * h
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

            w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
            inter = w1 * h1

            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= self.__nms_thresh)[0]
            order = order[inds + 1]
        return np.array(keep)

    @staticmethod
    def xywh2xyxy(x: np.ndarray) -> np.ndarray:
        y = np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y

    def post_process(
        self, input_data: list[np.ndarray]
    ) -> tuple[
        Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]
    ]:
        boxes, classes, scores = [], [], []
        for input, mask in zip(input_data, self.__masks):
            b, c, s = self.process(input, mask, self.__anchors)
            b, c, s = self.filter_boxes(b, c, s)
            boxes.append(b)
            classes.append(c)
            scores.append(s)

        boxes = np.concatenate(boxes)
        boxes = Rknn_yolov5s.xywh2xyxy(boxes)
        classes = np.concatenate(classes)
        scores = np.concatenate(scores)

        nboxes, nclasses, nscores = [], [], []
        for c in set(classes):
            inds = np.where(classes == c)
            b = boxes[inds]
            c = classes[inds]
            s = scores[inds]

            keep = self.nms_boxes(b, s)

            nboxes.append(b[keep])
            nclasses.append(c[keep])
            nscores.append(s[keep])

        if not nclasses and not nscores:
            return None, None, None

        return np.concatenate(nboxes), np.concatenate(nclasses), np.concatenate(nscores)

    def draw(
        self,
        frame: np.ndarray,
        boxes: np.ndarray,
        scores: np.ndarray,
        classes: np.ndarray
    ) -> np.ndarray:
        width, height = frame.shape[:2]
        x_modifier = width / self.__image_size[0]
        y_modifier = height / self.__image_size[1]

        for box in boxes:
            top, left, right, bottom = (
                abs(int(coord)) for coord in box
            )

            relative_top = int(top * y_modifier)
            relative_left = int(left * x_modifier)
            relative_right = int(right * y_modifier)
            relative_bottom = int(bottom * x_modifier)

            cv2.rectangle(frame, (relative_top, relative_left), (relative_right, relative_bottom), (255, 0, 0), 2)

        return frame
    
    def create_frame(
        self,
        frame: np.ndarray,
        boxes: np.ndarray,
        scores: np.ndarray,
        classes: np.ndarray
    ) -> np.ndarray:
        width, height = frame.shape[:2]
        empty_frame = np.zeros((width, height, 3), dtype=np.uint8)
        x_modifier = width / self.__image_size[0]
        y_modifier = height / self.__image_size[1]
        coords = []

        for box in boxes:
            top, left, right, bottom = (
                abs(int(coord)) for coord in box
            )

            relative_top = int(top * y_modifier)
            relative_left = int(left * x_modifier)
            relative_right = int(right * y_modifier)
            relative_bottom = int(bottom * x_modifier)

            cropped_region = frame[relative_top:relative_bottom, relative_left:relative_right]
            empty_frame[relative_top:relative_bottom, relative_left:relative_right] = cropped_region

        return empty_frame

    def detect(self, frame: np.ndarray) -> np.ndarray:
        model_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        model_frame = cv2.resize(model_frame, self.__image_size, interpolation=cv2.INTER_AREA)
        outputs = self.__rknn_model.inference(inputs=[model_frame])

        input0_data = outputs[0].reshape([3, -1] + list(outputs[0].shape[-2:]))
        input1_data = outputs[1].reshape([3, -1] + list(outputs[1].shape[-2:]))
        input2_data = outputs[2].reshape([3, -1] + list(outputs[2].shape[-2:]))

        input_data = list()
        input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input2_data, (2, 3, 0, 1)))

        boxes, classes, scores = self.post_process(input_data)

        if boxes is not None:
            frame = self.create_frame(frame, boxes, scores, classes)

        return frame
