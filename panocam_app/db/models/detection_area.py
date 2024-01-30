from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.exceptions import ValidationError

from panocam_app.db.models import Camera


def validate_shape(value):
    try:
        map(int, value.split("x"))
    except ValueError:
        raise ValidationError("Неверный формат shape. Используйте целые числа, разделенные 'x'.")


# TODO: add django-jsonform
class DetectionArea(models.Model):
    camera = models.ForeignKey(Camera, models.CASCADE, blank=True, null=False)
    label = models.TextField(max_length=30, blank=True, null=False)
    points = ArrayField(ArrayField(models.IntegerField()), blank=True, null=False)
    shape = models.CharField(max_length=15, validators=[validate_shape])

    class Meta:
        db_table = 'detection_area'
