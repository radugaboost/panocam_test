from django.db import models
from . import Camera

class Label(models.Model):
    camera = models.ForeignKey(Camera, models.CASCADE, blank=True, null=False)
    content = models.CharField(null=False, max_length=100)
    x_axing = models.DecimalField(max_digits=7, decimal_places=2, null=False, blank=True)
    y_axing = models.DecimalField(max_digits=7, decimal_places=2, null=False, blank=True)

    class Meta:
        db_table = 'label'

    def __str__(self):
        return f'{self.camera}'
