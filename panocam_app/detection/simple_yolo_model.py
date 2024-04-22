import numpy as np
import cv2
from inference import get_model
import supervision as sv
import os


class SimpleYolo:
    detections: sv.Detections

    __obj_thresh = 0.65
    __nms_thresh = 0.45
    __image_size = (640, 640)
    __similarity = 0.7
    counter = 0
    output_dir = './panocam_app/storage/detected_humans'
    color_ranges = {
        'white': ([0, 0, 200], [180, 50, 255]),
        'black': ([0, 0, 0], [180, 255, 60]),
        'green': ([35, 50, 50], [80, 255, 255]),
        'blue': ([90, 50, 50], [130, 255, 255]),
        'red': ([0, 50, 50], [10, 255, 255])
    }

    def __init__(
            self,
            model_id: int,
            npu_id: int = 0
    ) -> None:
        self.model_id = model_id
        self.__model = get_model(model_id='yolov8n-640')
        self.bounding_box_annotator = sv.BoundingBoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()

    def extract_dominant_color(self, image):
        resized_image = cv2.resize(image, self.__image_size)

        hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

        for color_name, (lower, upper) in SimpleYolo.color_ranges.items():
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv_image, lower, upper)
            if cv2.countNonZero(mask) > 0:
                return color_name

        return None

    @staticmethod
    def calculate_similarity(img1: np.ndarray, img2: np.ndarray):
        img1_resized = cv2.resize(img1, (img2.shape[1], img2.shape[0]))

        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
        return correlation[0, 0]

    def find_sim(self, color, cropped_object: np.ndarray):
        color_dir = os.path.join(self.output_dir, color)

        for filename in os.listdir(color_dir):
            existing_image = cv2.imread(os.path.join(self.output_dir, f'{color}/{filename}'))
            similarity = self.calculate_similarity(existing_image, cropped_object)
            print(similarity, os.path.join(self.output_dir, f'{color}/{filename}'))
            if similarity > self.__similarity:
                return True
        self.save_by_color(color, cropped_object)

    def save_by_color(self, color: str, cropped_object: np.ndarray):
        color_dir = os.path.join(self.output_dir, color)
        os.makedirs(color_dir, exist_ok=True)

        self.counter += 1
        filename = os.path.join(self.output_dir, f'{color}/object_{self.counter}.jpg')
        print(os.path.join(self.output_dir, f'{color}/{filename}'))
        cv2.imwrite(filename, cropped_object)

    def re_identify(self, frame: np.ndarray, detection: sv.Detections) -> bool:
        x, y, w, h = map(int, detection.xyxy.tolist()[0])
        cropped_object = frame[y:y + h, x:x + w]
        if cropped_object.size == 0:
            return False
        color = self.extract_dominant_color(cropped_object)

        if color is not None:
            return self.find_sim(color, cropped_object)
        return False

    def detect(self, frame: np.ndarray) -> tuple[np, np, np] | None:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(rgb_frame, self.__image_size, interpolation=cv2.INTER_AREA)

        self.detections = self.__model.infer(resized_frame)
        xyxy_list = []
        classes_list = []
        for detection in self.detections:
            detection = sv.Detections.from_inference(detection.dict(by_alias=True, exclude_none=True))
            if not detection:
                continue
            seen = self.re_identify(frame, detection)
            xyxy_list.append(detection.xyxy.tolist())
            classes_list.append(detection.class_id.tolist())
            print(list(map(int, detection.xyxy.tolist()[0][:2])))
            frame = self.bounding_box_annotator.annotate(scene=frame, detections=detection)
            cv2.putText(
                frame,
                'seen' if seen else '',
                list(map(int, detection.xyxy.tolist()[0][:2])),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )
        xyxy = np.concatenate(xyxy_list) if xyxy_list else np.empty((0, 4))
        classes = np.concatenate(classes_list) if classes_list else np.empty(0)
        return frame, xyxy, classes
