from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from ddm.models import IncomingFileMetaData, FileAlert, AlertDetial


def index(request):
    params  = {'name': 'yogesh'}
    return render(request, 'dashboard.html', params)

def alertData(request):
    if request.method == "POST":
        data = request.POST
        alert = AlertDetial() 
        alert.alertName = data.get("alertName")
        alert.alertInterestedParty = data.get("alertInterestedParty")
        alert.variations = data.get("variations")
        alert.active = data.get("active")
        alert.save()
    alert = AlertDetial.objects.all()
    params  = {'data': alert}
    return render(request, 'alert-data.html', params)
    

def FileMetaData(request):
    fileMetaData = IncomingFileMetaData.objects.all()
    params  = {'data': fileMetaData}
    return render(request, 'file-data.html', params)

