import os
from datetime import datetime
import sqlite3
import atexit
import sys
from time import time
import scipy.stats as stats
import numpy as np

g_dbCon = sqlite3.Connection
g_zscoreAlert = "ZSCORE_SIZE"
g_percentageSizeAlert = "PERCENTAGE_SIZE"
g_fileArrivalAlert = "FILE_ARRIVAL"
g_senderNotifyAlert = "SENDER_NOTIFY"
g_fileSizeLargeAlert = "FILE_SIZE_LARGE"
g_fileSizeSmallAlert = "FILE_SIZE_SMALL"
    
def exit_handler():
    print ('My application is ending!')
    g_dbCon.close()

def zscoreSizeAlert(cur, fetchedResult, resFileMetaDataList, alertProc):
    print("Processing ZScore Size Alert:")
    sizesList = []
    for obj in resFileMetaDataList:
        print (obj)
        sizesList.append(int(obj[1]))
                    
    sizeZScore = stats.zscore(sizesList)
    print(sizesList)
    print(sizeZScore)
                    
    zscoreLimit = int(alertProc[2])
    if sizeZScore[0] > zscoreLimit or sizeZScore[0] < -zscoreLimit:
        alertDesc = "The File {0} size {1}KB is outside the limit of +/-{2} confidence interval with the sample size of last four records.".format(fetchedResult[0], sizesList[0], zscoreLimit)
        print (alertDesc)
        cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_zscoreAlert, alertDesc))

def percentageSizeAlert(cur, fetchedResult, resFileMetaDataList, alertProc):
    print("Processing Percentage Size Alert:")
    if resFileMetaDataList and len(resFileMetaDataList) > 1:
        percentageOfSizeDiff = ((int(resFileMetaDataList[0][1]) / int(resFileMetaDataList[1][1])) * 100.0)-100
        print (resFileMetaDataList[0][1])
        print (resFileMetaDataList[1][1])
                
        percentageSizeLimit = int(alertProc[2])
        if percentageOfSizeDiff > percentageSizeLimit or percentageOfSizeDiff < -percentageSizeLimit:
            alertDesc = "The File {0} size {1}KB with percentage {2} is outside the limit of +/-{3} Percentage of last record.".format(fetchedResult[0], resFileMetaDataList[0][1], percentageOfSizeDiff, percentageSizeLimit)
            print (alertDesc)
            cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_percentageSizeAlert, alertDesc))

def fileArrivalAlert(cur, fetchedResult, alertProc):
    print("Processing File Arrival Alert:")
   
    fileArraivalVariation = str(alertProc[2]).split(',')
    if fileArraivalVariation and len(fileArraivalVariation) == 2:
        if fileArraivalVariation[0] == fetchedResult[0]:
            arrivalDiff = 0
            try:
                configuredTime = datetime.strptime(fileArraivalVariation[1], "%H:%M:%S")
                splitedTime = str(fetchedResult[1]).split(' ')
                splitedTimeWithoutMilliSec = splitedTime[1][:8]
                fileArrivalTime = datetime.strptime(splitedTimeWithoutMilliSec, "%H:%M:%S")
                arrivalDiff = int((fileArrivalTime - configuredTime).total_seconds())
            except Exception as inst:
                print (inst)
                arrivalDiff = 0
                                
            if arrivalDiff > 60 or arrivalDiff < -60:
                alertDesc = "The File {0} Arrival is delayed by {1} minutes".format(fetchedResult[0], int(arrivalDiff/60))
                print (alertDesc)
                cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_fileArrivalAlert, alertDesc))

def sendNotifyAlert(cur, fetchedResult, alertProc):
    print("Processing Send Notify Alert:")
    if alertProc[2] == fetchedResult[2]:
        alertDesc = "The File {0} sent by the sender {1}".format(fetchedResult[0], fetchedResult[2])
        print (alertDesc)
        cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_senderNotifyAlert, alertDesc))
        
def fileSizeLargeAlert(cur, fetchedResult, resFileMetaDataList, alertProc):
    print("Processing File size Large Alert:")
    if resFileMetaDataList and int(resFileMetaDataList[0][1]) > int(alertProc[2]):
        alertDesc = "The File {0} has the large size of {1}".format(fetchedResult[0], resFileMetaDataList[0][1])
        print (alertDesc)
        cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_fileSizeLargeAlert, alertDesc))

def fileSizeSmallAlert(cur, fetchedResult, resFileMetaDataList, alertProc):
    print("Processing File size small Alert:")
    if resFileMetaDataList and int(resFileMetaDataList[0][1]) < int(alertProc[2]):
        alertDesc = "The File {0} has the small size of {1}".format(fetchedResult[0], resFileMetaDataList[0][1])
        print (alertDesc)
        cur.execute("INSERT INTO FileAlerts VALUES(?, ?, ?)", (fetchedResult[0], g_fileSizeSmallAlert, alertDesc))
        
if __name__ == '__main__':
    atexit.register(exit_handler)
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    g_dbPath = curDirPath + "\\..\\db\\ddm.db"
    
    if not os.path.exists(g_dbPath):
       print("DB not exists.")
       sys.exit()
       
    g_dbCon = sqlite3.connect(g_dbPath)
    cur = g_dbCon.cursor()
    
    print ("Alert Processor has started.")
    
    resAlertDetialsCur = cur.execute("SELECT * FROM AlertDetials")
    resAlertDetialsList = resAlertDetialsCur.fetchall()
    
    while 1:
        resProcessData = cur.execute("SELECT * FROM ProcessData ORDER BY arrivalTime")
        fetchedResult = resProcessData.fetchone()
        if fetchedResult:
            print ("\nProcessing - %s - %s - %s" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            resFileMetaDataCur = cur.execute("SELECT arrivalTime, size FROM IncomingFileMetaData WHERE fileName = '%s' and sender = '%s' and arrivalTime <= '%s' ORDER BY arrivalTime desc LIMIT 4" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            resFileMetaDataList = resFileMetaDataCur.fetchall()
            
            for alertProc in resAlertDetialsList:
                if alertProc[0] == g_zscoreAlert and alertProc[3] == "1":
                    zscoreSizeAlert(cur, fetchedResult, resFileMetaDataList, alertProc)
                        
                if alertProc[0] == g_percentageSizeAlert and alertProc[3] == "1":
                    percentageSizeAlert(cur, fetchedResult, resFileMetaDataList, alertProc)
                
                if alertProc[0] == g_fileArrivalAlert and alertProc[3] == "1":
                    fileArrivalAlert(cur, fetchedResult, alertProc)
                
                if alertProc[0] == g_senderNotifyAlert and alertProc[3] == "1":
                    sendNotifyAlert(cur, fetchedResult, alertProc)
                
                if alertProc[0] == g_fileSizeLargeAlert and alertProc[3] == "1":
                    fileSizeLargeAlert(cur, fetchedResult, resFileMetaDataList, alertProc)
                    
                if alertProc[0] == g_fileSizeSmallAlert and alertProc[3] == "1":
                    fileSizeSmallAlert(cur, fetchedResult, resFileMetaDataList, alertProc)
                    
            cur.execute("DELETE FROM ProcessData WHERE fileName = '%s' and sender = '%s' and arrivalTime = '%s'" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            g_dbCon.commit()
        
    g_dbCon.close()