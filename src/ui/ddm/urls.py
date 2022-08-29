from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="dashboard"),
    path('alertData', views.alertData, name="alert_data"),
    path('fileData', views.FileMetaData, name="file_data"),
]
