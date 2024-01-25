from django.contrib.postgres.fields import ArrayField
from django.db import models

from panocam_app.db.models import Camera


# TODO: add django-jsonform
class DetectionArea(models.Model):
    camera = models.ForeignKey(Camera, models.CASCADE, blank=True, null=False)
    label = models.TextField(max_length=30, blank=True, null=False)
    points = ArrayField(ArrayField(models.IntegerField()), blank=True, null=False)

    class Meta:
        db_table = 'detection_area'
