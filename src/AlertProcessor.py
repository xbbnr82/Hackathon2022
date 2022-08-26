import os
from datetime import datetime
import sqlite3
import atexit
import scipy.stats as stats
import numpy as np

g_dbCon = sqlite3.Connection

def insertAlertInterestedParty(alertName, alertParty):
    cur = g_dbCon.cursor()
    cur.execute("INSERT INTO AlertDetials VALUES(?, ?)", (alertName, alertParty))
    g_dbCon.commit()
    
def exit_handler():
    print ('My application is ending!')
    g_dbCon.close()

if __name__ == '__main__':
    atexit.register(exit_handler)
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    g_dbPath = curDirPath + "\\..\\db\\ddm.db"
    g_dbCon = sqlite3.connect(g_dbPath)
    cur = g_dbCon.cursor()
    
    while 1:
        resProcessData = cur.execute("SELECT * FROM ProcessData ORDER BY arrivalTime")
        fetchedResult = resProcessData.fetchone()
        if fetchedResult:
            print ("\nProcessing - %s - %s - %s" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            resFileMetaDataList = cur.execute("SELECT arrivalTime, size FROM IncomingFileMetaData WHERE fileName = '%s' and sender = '%s' and arrivalTime <= '%s' ORDER BY arrivalTime LIMIT 4" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            sizesList = []
            for obj in resFileMetaDataList:
                print (obj)
                sizesList.append(int(obj[1]))
            
            sizesArray = np.asarray(sizesList)
            sizeZScore = stats.zscore(sizesArray)
            
            print(sizesList)
            print(sizeZScore)
            
            cur.execute("DELETE FROM ProcessData WHERE fileName = '%s' and sender = '%s' and arrivalTime = '%s'" % (fetchedResult[0], fetchedResult[2], fetchedResult[1]))
            g_dbCon.commit()
        
    g_dbCon.close()