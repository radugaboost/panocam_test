from django.db import models
from django.contrib.auth.models import User


class Configuration(models.Model):
    name = models.CharField(null=False, max_length=24)
    sharpness = models.IntegerField(null=False, default=100)
    resolution = models.CharField(null=False, max_length=20)
    brightness = models.IntegerField(null=False, default=100)
    saturation = models.IntegerField(null=False, default=100)
    contrast = models.IntegerField(null=False, default=100)
    smoothing = models.IntegerField(null=False, default=100)
    frame_rate = models.IntegerField(null=False, default=100)
    hue = models.IntegerField(null=False, default=100)

    class Meta:
        db_table = 'configuration'


class Camera(models.Model):
    ip = models.CharField(null=False, max_length=24)
    mask = models.CharField(null=False, max_length=24)
    name = models.CharField(null=False, max_length=30)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=False)
    image_config = models.ForeignKey(Configuration, models.DO_NOTHING, blank=True, null=False)

    class Meta:
        db_table = 'camera'


class Label(models.Model):
    camera = models.ForeignKey(Camera, models.CASCADE, blank=True, null=False)
    content = models.CharField(null=False, max_length=100)
    x_axing = models.DecimalField(max_digits=7, decimal_places=2, null=False, blank=True)
    y_axing = models.DecimalField(max_digits=7, decimal_places=2, null=False, blank=True)
    
    class Meta:
        db_table = 'label'

