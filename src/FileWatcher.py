import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys
from datetime import datetime
from pathlib import Path
import configparser
import sqlite3
import pandas as pd

g_pathInbound = ""
g_pathArchive = ""
g_dbPath = ""
g_dbCon = sqlite3.Connection

class Watcher:
    pathToWatch = ""

    def __init__(self):
        self.pathToWatch = str(g_pathInbound)
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.pathToWatch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print ("Error")

        self.observer.join()
        
def insertIncomingFileMetaData(fileName, fileArrivalTime, fileSize, fileSender, fileNoOfRecords):
    cur = g_dbCon.cursor()
    cur.execute("INSERT INTO IncomingFileMetaData VALUES(?, ?, ?, ?, ?)", (fileName, fileArrivalTime, fileSize, fileSender, fileNoOfRecords))
    g_dbCon.commit()
    
class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        else:
            print ("Received event - %s, path - %s" %(event.event_type, event.src_path))
            if event.event_type == "created" and os.path.exists(event.src_path):
                fileName = Path(event.src_path).stem
                fileExt = Path(event.src_path).suffix.replace('.','')
                fileSize = os.path.getsize(event.src_path)
                fileArrivalTime = datetime.fromtimestamp(os.path.getctime(event.src_path)).strftime('%Y%m%d%H%M%S')
                fileNameSplit = fileName.split('_')[-1]
                fileNoOfRecords = 0
                
                if len(fileNameSplit) == len(fileName):
                    fileSender = "DEFAULT"
                else:
                    fileSender = fileNameSplit
                
                if fileExt.lower() == "csv":
                    fileNoOfRecords = len(pd.read_csv(event.src_path).index)
                    
                print("File name - %s" % fileName)
                print("File arrival time - %s" % fileArrivalTime)
                print("File size - %s" % fileSize)
                print("File sender - %s" % fileSender)
                print("File no of records - %s" % fileNoOfRecords)
                
                insertIncomingFileMetaData(fileName, fileArrivalTime, fileSize, fileSender, fileNoOfRecords)
                

if __name__ == '__main__':
    config = configparser.ConfigParser()
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    iniPath = curDirPath + "\\..\\props\\settings.ini"
    dataset = config.read(iniPath)
    
    if len(dataset) != 1:
        print("Failed to open/find config file")
        sys.exit()
    
    g_pathInbound = config['watcher']['inboundfolder'].strip('\"')
    if not os.path.exists(g_pathInbound):
        print("Inbound Directory not exists")
        sys.exit()
        
    g_pathArchive = config['watcher']['archive'].strip('\"')
    if not os.path.exists(g_pathArchive):
        print("Arcive Directory not exists")
        sys.exit()
        
    g_dbPath = curDirPath + "\\..\\db\\ddm.db"
    
    if not os.path.exists(g_dbPath):
       print("DB not exists.")
       sys.exit()
       
    g_dbCon = sqlite3.connect(g_dbPath)
    
    w = Watcher()
    w.run()