from cv2 import (
    hconcat, vconcat,
    INTER_CUBIC, resize
)
from numpy import ndarray


def vconcat_resize(
        images: ndarray[dict],
        interpolation: int = INTER_CUBIC
    ) -> ndarray: 
    w_min = min(img.shape[1] for img in images) 

    resized_images = [
        resize(
            img,
            (w_min, int(img.shape[0] * w_min / img.shape[1])),
            interpolation=interpolation
        ) 
        for img in images
    ]

    return vconcat(resized_images) 


def hconcat_resize(
        input_images: ndarray[dict], 
        interpolation: int = INTER_CUBIC
    ) -> ndarray:
    h_min = float('inf')
    images = list()

    for content in input_images:
        image = content.get('image')
        h_min = min(h_min, image.shape[0])
        images.append(image)

    resized_images = [
        resize(
            img,
            (int(img.shape[1] * h_min / img.shape[0]), h_min),
            interpolation=interpolation
        )  
        for img in images
    ]

    return hconcat(resized_images)


def concat_resize(
        content: list[ndarray[dict]],
        interpolation: int = INTER_CUBIC
    ) -> ndarray:
    h_resized_images = [
        hconcat_resize(images, interpolation=INTER_CUBIC)  
        for images in content
    ]

    return vconcat_resize(h_resized_images, interpolation=INTER_CUBIC)
