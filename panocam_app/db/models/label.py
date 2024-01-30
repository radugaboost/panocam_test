from django.db import models
from . import Camera


class Label(models.Model):
    content = models.CharField(null=False, max_length=100)

    class Meta:
        db_table = 'label'
