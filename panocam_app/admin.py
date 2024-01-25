from django.contrib import admin
from panocam_app.db.models import (
    Configuration, Camera, DetectionModel,
    VideoRecord, Label, DetectionArea
)

admin.site.register(Configuration)
admin.site.register(Camera)
admin.site.register(DetectionModel)
admin.site.register(VideoRecord)
admin.site.register(Label)
admin.site.register(DetectionArea)
