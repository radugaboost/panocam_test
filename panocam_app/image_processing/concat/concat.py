from .utils.resize import concat_resize
import numpy as np


def split_images(
        images: list[dict],
        max_per_group: int = 6
    ) -> list[np.ndarray[dict]]:
    total_elements = len(images)

    if total_elements <= max_per_group:
        max_per_group //= 2

    num_groups = int(np.ceil(total_elements / max_per_group))
    grouped_list = np.array_split(images, num_groups)

    return [group for group in grouped_list]


def concat_images(images: list[dict]) -> np.ndarray:
    groups = split_images(images)
    return concat_resize(groups)
