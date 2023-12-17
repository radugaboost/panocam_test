from django.db import models

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

    def __str__(self):
        return f'{self.name}'