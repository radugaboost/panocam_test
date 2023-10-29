import cv2
import numpy as np
from rknnlite.api import RKNNLite

class Rknn_yolov5s:

    CLASSES = (
        "person", "bicycle", "car", "motorbike ", "aeroplane ", "bus ", "train", "truck ", "boat", 
        "traffic light", "fire hydrant", "stop sign ", "parking meter", "bench", "bird", "cat", 
        "dog ", "horse ", "sheep", "cow", "elephant", "bear", "zebra ", "giraffe", "backpack", 
        "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", 
        "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", 
        "wine glass", "cup", "fork", "knife ", "spoon", "bowl", "banana", "apple", "sandwich", "orange", 
        "broccoli", "carrot", "hot dog", "pizza ", "donut", "cake", "chair", "sofa", "pottedplant",
        "bed", "diningtable", "toilet ", "tvmonitor", "laptop	", "mouse	", "remote ", "keyboard ", 
        "cell phone", "microwave ", "oven ", "toaster", "sink", "refrigerator ", "book", "clock", 
        "vase", "scissors ", "teddy bear ", "hair drier", "toothbrush "
    )
    OBJ_THRESH = 0.25
    NMS_THRESH = 0.45
    IMAGE_SIZE = (640, 640)
    OBJECT_IMAGE_SIZE = (64, 64)
    MASKS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8]
    ]
    ANCHORS = [
        [10, 13], [16, 30], [33, 23],
        [30, 61], [62, 45],[59, 119],
        [116, 90], [156, 198], [373, 326]
    ]

    def __init__(
            self,
            rknn_model: str,
            output_frame_size: tuple = (1280, 720)
        ) -> None:
        self.rknn_model = Rknn_yolov5s.initRKNN(rknn_model)
        self.output_frame_size = output_frame_size

    @staticmethod
    def initRKNN(rknnModel: str):
        rknn_lite = RKNNLite()
        ret = rknn_lite.load_rknn(rknnModel)
        if ret != 0:
            print("Load RKNN rknnModel failed")
            exit(ret)
        ret = rknn_lite.init_runtime()
        if ret != 0:
            print("Init runtime environment failed")
            exit(ret)
        print(rknnModel, "\t\tdone")
        return rknn_lite

    @staticmethod
    def process(input, mask, anchors):

        anchors = [anchors[i] for i in mask]
        grid_h, grid_w = map(int, input.shape[0:2])

        box_confidence = input[..., 4]
        box_confidence = np.expand_dims(box_confidence, axis=-1)

        box_class_probs = input[..., 5:]

        box_xy = input[..., :2] *2 - 0.5

        col = np.tile(np.arange(0, grid_w), grid_w).reshape(-1, grid_w)
        row = np.tile(np.arange(0, grid_h).reshape(-1, 1), grid_h)
        col = col.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        row = row.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        grid = np.concatenate((col, row), axis=-1)
        box_xy += grid
        box_xy *= int(Rknn_yolov5s.IMAGE_SIZE[0] / grid_h)

        box_wh = pow(input[..., 2:4] *2, 2)
        box_wh = box_wh * anchors

        return np.concatenate((box_xy, box_wh), axis=-1), box_confidence, box_class_probs

    @staticmethod
    def filter_boxes(boxes, box_confidences, box_class_probs):
        boxes = boxes.reshape(-1, 4)
        box_confidences = box_confidences.reshape(-1)
        box_class_probs = box_class_probs.reshape(-1, box_class_probs.shape[-1])

        _box_pos = np.where(box_confidences >= Rknn_yolov5s.OBJ_THRESH)
        boxes = boxes[_box_pos]
        box_confidences = box_confidences[_box_pos]
        box_class_probs = box_class_probs[_box_pos]

        class_max_score = np.max(box_class_probs, axis=-1)
        classes = np.argmax(box_class_probs, axis=-1)
        _class_pos = np.where(class_max_score >= Rknn_yolov5s.OBJ_THRESH)

        return boxes[_class_pos], classes[_class_pos], (class_max_score * box_confidences)[_class_pos]

    @staticmethod
    def nms_boxes(boxes, scores):
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
            inds = np.where(ovr <= Rknn_yolov5s.NMS_THRESH)[0]
            order = order[inds + 1]
        return np.array(keep)
    
    @staticmethod
    def xywh2xyxy(x):
        # Convert [x, y, w, h] to [x1, y1, x2, y2]
        y = np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y


    def post_process(self, input_data):
        boxes, classes, scores = [], [], []
        for input, mask in zip(input_data, Rknn_yolov5s.MASKS):
            b, c, s = Rknn_yolov5s.process(input, mask, Rknn_yolov5s.ANCHORS)
            b, c, s = Rknn_yolov5s.filter_boxes(b, c, s)
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

            keep = Rknn_yolov5s.nms_boxes(b, s)

            nboxes.append(b[keep])
            nclasses.append(c[keep])
            nscores.append(s[keep])

        if not nclasses and not nscores:
            return None, None, None

        return np.concatenate(nboxes), np.concatenate(nclasses), np.concatenate(nscores)

    def draw(self, frame, boxes, scores, classes):
        frame_height = Rknn_yolov5s.IMAGE_SIZE[0]
        frame_width = Rknn_yolov5s.IMAGE_SIZE[1]
        combined_height = frame_height + Rknn_yolov5s.OBJECT_IMAGE_SIZE[0]
        combined_frame = np.zeros((combined_height, frame_width, 3), dtype=np.uint8)
        resized_objects = []

        clone_frame = frame.copy()
        for box, _, _ in zip(boxes, scores, classes):
            top, left, right, bottom = (abs(int(coord)) for coord in box)
            top = abs(top)
            print(box)
            object_image = clone_frame[left:bottom, top:right]
            resized_object = cv2.resize(object_image, Rknn_yolov5s.OBJECT_IMAGE_SIZE)
            resized_objects.append(resized_object)
            cv2.rectangle(frame, (top, left), (right, bottom), (255, 0, 0), 2)

        current_x = 0
        init_frame_height = frame_height
        for object_image in resized_objects:
            object_width = object_image.shape[1]
            if current_x + object_width > frame_width:
                frame_height += object_image.shape[1]
                prev_height = combined_height
                combined_height += object_image.shape[1]
                new_combined_frame = np.zeros((combined_height, frame_width, 3), dtype=np.uint8)
                new_combined_frame[:prev_height, :frame_width] = combined_frame
                combined_frame = new_combined_frame
                current_x = 0

            combined_frame[frame_height:combined_height, current_x:current_x + object_width] = object_image
            current_x += object_width # сдвигаем текущее положение

        combined_frame[:init_frame_height, :frame_width] = frame
        combined_frame = cv2.resize(combined_frame, self.output_frame_size)
        return combined_frame

    def letterbox(im, new_shape=(640, 640), color=(0, 0, 0)):
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
            new_unpad[1]  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right,
                                cv2.BORDER_CONSTANT, value=color)  # add border
        return im
        # return im, ratio, (dw, dh)

    def detect(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, Rknn_yolov5s.IMAGE_SIZE)
        outputs = self.rknn_model.inference(inputs=[frame])

        input0_data = outputs[0].reshape([3, -1]+list(outputs[0].shape[-2:]))
        input1_data = outputs[1].reshape([3, -1]+list(outputs[1].shape[-2:]))
        input2_data = outputs[2].reshape([3, -1]+list(outputs[2].shape[-2:]))

        input_data = list()
        input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))
        input_data.append(np.transpose(input2_data, (2, 3, 0, 1)))

        boxes, classes, scores = self.post_process(input_data)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if boxes is not None:
            return self.draw(frame, boxes, scores, classes)

        return cv2.resize(frame, self.output_frame_size)