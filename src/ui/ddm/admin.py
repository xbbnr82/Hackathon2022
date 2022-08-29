from django.contrib import admin
from .models import IncomingFileMetaData, FileAlert, AlertDetial, ProcessData

# Register your models here.
admin.site.register(IncomingFileMetaData)
admin.site.register(FileAlert)
admin.site.register(AlertDetial)
admin.site.register(ProcessData)