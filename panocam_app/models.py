from django.db import models

class Configuration(models.Model):
    name = models.CharField(null=False, max_length=24)
    width = models.IntegerField(null=False, default=100)
    height = models.IntegerField(null=False, default=100)
    brightness = models.IntegerField(null=False, default=100)
    saturation = models.IntegerField(null=False, default=100)
    contrast = models.IntegerField(null=False, default=100)
    fps_rate = models.IntegerField(null=False, default=100)
    hue = models.IntegerField(null=False, default=100)

    class Meta:
        db_table = 'configuration'

class Camera(models.Model):
    ip = models.CharField(null=False, max_length=24)
    image_config = models.ForeignKey(
        Configuration,
        models.DO_NOTHING,
        blank=True,
        null=False,
    )
    
    class Meta:
        db_table = 'camera'
