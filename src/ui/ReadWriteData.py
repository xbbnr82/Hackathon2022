import os
from datetime import datetime
import sqlite3
import atexit
import sys
from time import time
import scipy.stats as stats
import numpy as np

g_dbCon = sqlite3.Connection

curDirPath = os.path.dirname(os.path.realpath(__file__))
g_dbPath = curDirPath + "\\..\\..\\db\\ddm.db"
if not os.path.exists(g_dbPath):
    print("DB not exists.")
    sys.exit()
    
g_dbCon = sqlite3.connect(g_dbPath, check_same_thread=False)
cur = g_dbCon.cursor()

def getFileAlertData():
    result = {}
    try:
        resProcessData = cur.execute("SELECT * FROM FileAlerts")
        result = resProcessData.fetchall()
    except Exception as ex:
        print (ex)
    return result

def getAlertData():
    result = {}
    try:
        resProcessData = cur.execute("SELECT * FROM AlertDetials")
        result = resProcessData.fetchall()
    except Exception as ex:
        print (ex)
    print(type(result))
    return result

def insertAlertData(alertName, alertParty, variations, active):
    cur.execute("INSERT INTO AlertDetials VALUES(?, ?, ?, ?)", (alertName, alertParty, variations, active))
    g_dbCon.commit()
    result = {}
    try:
        resProcessData = cur.execute("SELECT * FROM AlertDetials")
        result = resProcessData.fetchall()
    except Exception as ex:
        print (ex)
    return result

def getFileData():
    result = {}
    try:
        resProcessData = cur.execute("SELECT * FROM IncomingFileMetaData")
        result = resProcessData.fetchall()
    except Exception as ex:
        print (ex)
    return result
