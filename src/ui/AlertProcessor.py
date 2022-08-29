import os
from datetime import datetime
import atexit
from time import time
import scipy.stats as stats
import numpy as np
from ddm.models import IncomingFileMetaData, FileAlert, AlertDetial, ProcessData
import threading

g_zscoreAlert = "ZSCORE_SIZE"
g_percentageSizeAlert = "PERCENTAGE_SIZE"
g_fileArrivalAlert = "FILE_ARRIVAL"

def AlertProcessor():
    print ("Alert Processor has started.")
    resAlertDetialsList = AlertDetial.objects.all()
    while 1:
        fetchedResult = ProcessData.objects.all().order_by('arrivalTime').first()
        if fetchedResult:
            print ("\nProcessing - %s - %s - %s" % (fetchedResult.fileName, fetchedResult.sender, fetchedResult.arrivalTime))
            resFileMetaDataList = IncomingFileMetaData.objects.all().filter(fileName=fetchedResult.fileName, sender=fetchedResult.sender, arrivalTime=fetchedResult.arrivalTime).order_by('-arrivalTime')[:5] 
            for alertProc in resAlertDetialsList:
                if alertProc.alertName == g_zscoreAlert and alertProc.active == "1":
                    sizesList = []
                    for obj in resFileMetaDataList:
                        print (obj)
                        sizesList.append(int(obj.size))
                    
                    sizeZScore = stats.zscore(sizesList)
                    print(sizesList)
                    print(sizeZScore)
                    zscoreLimit = int(alertProc.variations)
                    if sizeZScore[0] > zscoreLimit or sizeZScore[0] < -zscoreLimit:
                        alertDesc = "The File {0} size {1}KB is outside the limit of +/-{2} confidence interval with the sample size of last four records.".format(fetchedResult.fileName, sizesList[0], zscoreLimit)
                        print (alertDesc)
                        fileAlert = FileAlert()
                        fileAlert.fileName = fetchedResult.fileName
                        fileAlert.alertName = g_zscoreAlert
                        fileAlert.alertDesc = alertDesc
                        fileAlert.save()

                if alertProc.alertName == g_percentageSizeAlert and alertProc.active == "1":
                    percentageOfSizeDiff = ((int(resFileMetaDataList[0][1]) / int(resFileMetaDataList[1][1])) * 100.0)-100
                    print (resFileMetaDataList[0][1])
                    print (resFileMetaDataList[1][1])
            
                    percentageSizeLimit = int(alertProc.variations)
                    if percentageOfSizeDiff > percentageSizeLimit or percentageOfSizeDiff < -percentageSizeLimit:
                        alertDesc = "The File {0} size {1}KB with percentage {2} is outside the limit of +/-{3} Percentage of last record.".format(fetchedResult.fileName, sizesList[0], percentageOfSizeDiff, percentageSizeLimit)
                        print (alertDesc)
                        fileAlert = FileAlert()
                        fileAlert.fileName = fetchedResult.fileName
                        fileAlert.alertName = g_percentageSizeAlert
                        fileAlert.alertDesc = alertDesc
                        fileAlert.save()
                        
                if alertProc.alertName == g_fileArrivalAlert and alertProc.active == "1":
                    percentageOfSizeDiff = ((int(resFileMetaDataList[0][1]) / int(resFileMetaDataList[1][1])) * 100.0)-100
                    print (fetchedResult.fileName)
                    print (fetchedResult.arrivalTime)
            
                    fileArraivalVariation = str(alertProc.variations).split(',')
                    if fileArraivalVariation and len(fileArraivalVariation) == 2:
                        if fileArraivalVariation[0] == fetchedResult.fileName:
                            arrivalDiff = 0
                            try:
                                configuredTime = datetime.strptime(fileArraivalVariation[1], "%H:%M:%S")
                                splitedTime = str(fetchedResult.arrivalTime).split(' ')
                                splitedTimeWithoutMilliSec = splitedTime[1][:8]
                                fileArrivalTime = datetime.strptime(splitedTimeWithoutMilliSec, "%H:%M:%S")
                                arrivalDiff = int((fileArrivalTime - configuredTime).total_seconds())
                            except Exception as inst:
                                print (inst)
                                arrivalDiff = 0
                                 
                            if arrivalDiff > 60 or arrivalDiff < -60:
                                alertDesc = "The File {0} Arrival is delayed by {1} minutes".format(fetchedResult.fileName, int(arrivalDiff/60))
                                print (alertDesc)
                                fileAlert = FileAlert()
                                fileAlert.fileName = fetchedResult.fileName
                                fileAlert.alertName = g_fileArrivalAlert
                                fileAlert.alertDesc = alertDesc
                                fileAlert.save()
            fetchedResult.delete()


def start():
    t1 = threading.Thread(name='AlertProcessor',target=AlertProcessor)
    t1.start()
