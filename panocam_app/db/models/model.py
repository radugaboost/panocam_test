from django.db import models


class DetectionModel(models.Model):
    name = models.CharField(null=False, max_length=255)
    description = models.CharField(null=False, max_length=255)
    file_path = models.CharField(null=False, max_length=255)
    active = models.BooleanField(default=False)

    class Meta:
        db_table = 'detection_model'

    def __str__(self):
        return f'{self.name} | active: {self.active}'
