import os
from datetime import datetime
import sqlite3
import atexit
import sys

g_dbCon = sqlite3.Connection

def createTable():
     con = sqlite3.connect(g_dbPath)
     cur = con.cursor()
     cur.execute("CREATE TABLE IncomingFileMetaData(fileName, arrivalTime DATETIME, size, sender)")
     cur.execute("CREATE TABLE FileAlerts(fileName, alertName, alertDesc)")
     cur.execute("CREATE TABLE AlertDetials(alertName, alertInterestedParty, variations, active)")
     cur.execute("CREATE TABLE ProcessData(fileName, arrivalTime DATETIME, sender)")
     con.commit()
     
     
def insertAlertInterestedParty(alertName, alertParty, variations, active):
    cur = g_dbCon.cursor()
    cur.execute("INSERT INTO AlertDetials VALUES(?, ?, ?, ?)", (alertName, alertParty, variations, active))
    g_dbCon.commit()
    
def exit_handler():
    print ('Application is ending!')
    g_dbCon.close()
     
if __name__ == '__main__':
    atexit.register(exit_handler)
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    g_dbPath = curDirPath + "\\..\\db\\"
    
    pathExists = os.path.exists(g_dbPath)
    if pathExists == False:
        os.mkdir(g_dbPath)
        
    g_dbPath = g_dbPath + "ddm.db"
    
    pathExists = os.path.exists(g_dbPath)
     
    if pathExists == False:
       createTable()
       
    g_dbCon = sqlite3.connect(g_dbPath)
       
    print("\nAdd Alert interested party\n")
    
    addMore = 'y'
    while addMore.lower() == 'y':
        alertName = input("Alert Name:")
        alertParty = input("Party:")
        variations = input("variations:")
        active = input("active:")
        insertAlertInterestedParty(alertName, alertParty, variations, active)
        addMore = input("Add more records (Y/N): ")
        
    g_dbCon.close()
