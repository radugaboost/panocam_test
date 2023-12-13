from django.contrib import admin
from . import models

admin.site.register(models.Configuration)
admin.site.register(models.Camera)
admin.site.register(models.DetectionModel)
admin.site.register(models.VideoRecord)

# Register your models here.
