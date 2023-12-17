from django.db import models
from django.contrib.auth.models import User
from .config import Configuration

class Camera(models.Model):
    ip = models.CharField(null=False, max_length=240)
    mask = models.CharField(null=False, max_length=24)
    name = models.CharField(null=False, max_length=30)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=False)
    image_config = models.ForeignKey(Configuration, models.DO_NOTHING, blank=True, null=False)
    is_recording = models.BooleanField(default=False)

    class Meta:
        db_table = 'camera'

    def __str__(self):
        return f'{self.name} | ip: {self.ip}'