from numpy import ndarray


def insert_into_center(
        frame: ndarray, insert_frame: ndarray
    ) -> ndarray:
    insert_h, insert_w = insert_frame.shape[:2]
    h, w = frame.shape[:2]

    diff_h, diff_w = (h - insert_h) // 2, (w - insert_w) // 2

    frame[diff_h: diff_h + insert_h, diff_w: diff_w + insert_w] = insert_frame
    return frame
