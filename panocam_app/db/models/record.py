from django.db import models
from django.utils import timezone

class VideoRecord(models.Model):
    name = models.CharField(max_length=100, default=timezone.now)
    start = models.DateTimeField(null=False, default=timezone.now)
    end = models.DateTimeField(null=True)
    saving_path = models.CharField(max_length=200, default=timezone.now)

    class Meta:
        db_table = 'video_record'

    def __str__(self):
        return f'{self.name}'