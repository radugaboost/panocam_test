import numpy as np
from cv2 import fillPoly, bitwise_and


def select_area(area: list, frame: np.ndarray) -> np.ndarray:
    borders = area[0]
    points = area[1]

    mask = np.zeros(frame.shape, dtype=np.uint8)
    roi_corners = np.array(points, dtype=np.int32)
    channel_count = frame.shape[2]
    ignore_mask_color = (255,) * channel_count
    fillPoly(mask, [roi_corners], ignore_mask_color)
    masked_image = bitwise_and(frame, mask)

    top, left = borders[0], borders[1]
    width = borders[2] - left
    height = borders[3] - top

    return masked_image[top:top + height, left:left + width]
