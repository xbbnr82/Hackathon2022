from django.db import models


class IncomingFileMetaData(models.Model):
    fileName =  models.CharField(max_length=200)
    arrivalTime = models.DateTimeField(auto_now_add=True)
    size =  models.IntegerField(default=0)
    sender = models.CharField(max_length=200)

class FileAlert(models.Model):
    fileName  = models.CharField(max_length=200)
    alertName = models.CharField(max_length=200)
    alertDesc = models.CharField(max_length=1000)

class AlertDetial(models.Model):
    alertName = models.CharField(max_length=200)
    alertInterestedParty = models.CharField(max_length=200)
    variations = models.CharField(max_length=500)
    active = models.IntegerField(default=1)
    
class ProcessData(models.Model):
    fileName = models.CharField(max_length=200)
    arrivalTime = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=200)