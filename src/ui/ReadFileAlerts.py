import os
from datetime import datetime
import sqlite3
import atexit
import sys

g_dbCon = sqlite3.Connection

def exit_handler():
    print ('My application is ending!')
    g_dbCon.close()
    
if __name__ == '__main__':
    atexit.register(exit_handler)
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    g_dbPath = curDirPath + "\\..\\..\\db\\"
    
    pathExists = os.path.exists(g_dbPath)
    if pathExists == False:
        os.mkdir(g_dbPath)
        
    g_dbPath = g_dbPath + "ddm.db"
    
    pathExists = os.path.exists(g_dbPath)
    
    if pathExists == True:
        g_dbCon = sqlite3.connect(g_dbPath)
        cur = g_dbCon.cursor()
        lastAlertRowid = 0
        
        while 1:
            resProcessData = cur.execute("SELECT rowid, * FROM FileAlerts WHERE rowid > '%s'" % lastAlertRowid)
            fetchedResult = resProcessData.fetchall()
            
            if fetchedResult:
                for alert in fetchedResult:
                    curRowId = int(alert[0])
                    if lastAlertRowid < curRowId:
                        print (alert)
                        lastAlertRowid = curRowId
            
    else:
        print ("Db path not found.")
