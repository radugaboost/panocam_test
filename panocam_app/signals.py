from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from .models import Camera, Configuration
from .scripts import start_all_cameras, THREADED_CAMERAS
from .views import get_available_cameras

def camera_restart(camera_id: int):
    if camera_id in THREADED_CAMERAS.keys():
        thread = THREADED_CAMERAS[camera_id]
        thread.restart()

@receiver(class_prepared)
def process_start(sender, **kwargs):
    start_all_cameras()

@receiver(post_save, sender=Camera)
def camera_configuration_updated(sender, instance, **kwargs):
    camera_restart(instance.id)

@receiver(post_save, sender=Configuration)
def camera_configuration_assigned(sender, instance, **kwargs):
    cameras = Camera.objects.filter(image_config=instance)
    for camera in cameras:
        camera_restart(camera.id)