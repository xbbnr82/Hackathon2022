from django.urls import path
from . import views

urlpatterns = [
    path('', views.FileAlertData, name="file_alert_data"),
    path('alertData', views.alertData, name="alert_data"),
    path('fileAlertData', views.FileAlertData, name="file_alert_data"),
]
