from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from panocam_app.models import (
    Camera, Configuration, DetectionModel
)
from panocam_app.scripts import (
    start_camera, start_all_cameras,
    THREADED_CAMERAS, ModelManager
)


def camera_restart(camera_id: int) -> None:
    thread = THREADED_CAMERAS[camera_id]
    started = thread.restart()
    if not started:
        del THREADED_CAMERAS[camera_id]


@receiver(class_prepared)
def process_start(sender, **kwargs) -> None:
    start_all_cameras()


@receiver(post_save, sender=Camera)
def camera_configuration_updated(sender, instance, **kwargs) -> None:
    cam_id = instance.id
    camera = THREADED_CAMERAS.get(cam_id)
    if camera:
        camera_restart(cam_id)
    else:
        start_camera(cam_id)


@receiver(post_save, sender=Configuration)
def camera_configuration_assigned(sender, instance, **kwargs) -> None:
    cameras = Camera.objects.filter(image_config=instance)
    for camera in cameras:
        camera_restart(camera.id)


@receiver(post_save, sender=DetectionModel)
def update_models_on_save(sender, instance, **kwargs) -> None:
    ModelManager.update_models()
