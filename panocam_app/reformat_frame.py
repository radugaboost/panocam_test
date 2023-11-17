import cv2
import numpy as np


def distortion_func(x, width):
    return 1 / 5100 * (x - width // 2) ** 2


def warp_image(img, min_divisions=20):
    height, img_width = img.shape[:2]

    num_divisions = min(min_divisions, img_width)
    part_width = img_width // num_divisions

    parts = []
    for i in range(num_divisions):
        part_start = i * part_width
        part_end = (i + 1) * part_width if i < num_divisions - 1 else img_width
        parts.append(img[:, part_start:part_end])

    warped_parts = []
    height, width = parts[0].shape[:2]
    for i, part in enumerate(parts):
        pts1 = np.float32([(0, height), (0, distortion_func(i * width, img_width)),
                           (width, distortion_func((i + 1) * width, img_width)), (width, height)])
        pts2 = np.float32([(0, height), (0, 0), (width, 0), (width, height)])

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped_part = cv2.warpPerspective(part, matrix, (width, height))
        warped_parts.append(warped_part)

    result = np.hstack(warped_parts)

    return result


def start_streem():
    cv2.namedWindow('Warped Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Warped Video', 640, 480)
    cv2.namedWindow('Input Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Input Video', 640, 480)
    video_capture = cv2.VideoCapture('rtsp://admin:F56-sdfw6732@77.232.155.123')

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        result_frame = warp_image(frame)

        cv2.imshow('Warped Video', result_frame)
        cv2.imshow('Input Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    start_streem()
