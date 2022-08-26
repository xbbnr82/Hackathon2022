import os
from datetime import datetime
import sqlite3
import atexit
import sys

g_dbCon = sqlite3.Connection

def createTable():
     con = sqlite3.connect(g_dbPath)
     cur = con.cursor()
     cur.execute("CREATE TABLE IncomingFileMetaData(fileName, arrivalTime, size, sender)")
     cur.execute("CREATE TABLE FileAlerts(fileName, alertName, alertDesc)")
     cur.execute("CREATE TABLE AlertDetials(alertName, alertInterestedParty)")
     con.commit()
     
     
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
     
    if not os.path.exists(g_dbPath):
       createTable()
       
    g_dbCon = sqlite3.connect(g_dbPath)
       
    print("\nAdd Alert interested party\n")
    
    addMore = 'Y'
    while addMore == 'Y':
        alertName = input("Alert Name:")
        alertParty = input("Party:")
        insertAlertInterestedParty(alertName, alertParty)
        addMore = input("Add more records (Y/N): ")
        
    g_dbCon.close()
