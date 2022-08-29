from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from ReadWriteData import getAlertData, getFileData , insertAlertData, getFileAlertData


def index(request):
    params  = {'name': 'yogesh'}
    return render(request, 'dashboard.html', params)

def alertData(request):
    if request.method == "POST":
        data = request.POST
        insertAlertData(data.get("alertName"), data.get("alertInterestedParty"), data.get("variations"), data.get("active"))
    alert = getAlertData()
    params  = {'data': alert}
    return render(request, 'alert-data.html', params)
    

def FileMetaData(request):
    fileMetaData = getFileData()
    params  = {'data': fileMetaData}
    return render(request, 'file-data.html', params)

def FileAlertData(request):
    fileMetaData = getFileAlertData()
    params  = {'data': fileMetaData}
    return render(request, 'file-alert-data.html', params)

