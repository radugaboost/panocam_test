from django.contrib import admin
from . import models

admin.site.register(models.Configuration)
admin.site.register(models.Camera)
admin.site.register(models.DetectionModel)

# Register your models here.
