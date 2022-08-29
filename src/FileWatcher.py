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
import shutil

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
        
def insertIncomingFileMetaData(fileName, fileArrivalTime, fileSize, fileSender):
    cur = g_dbCon.cursor()
    cur.execute("INSERT INTO IncomingFileMetaData VALUES(?, ?, ?, ?)", (fileName, fileArrivalTime, fileSize, fileSender))
    cur.execute("INSERT INTO ProcessData VALUES(?, ?, ?)", (fileName, fileArrivalTime, fileSender))
    g_dbCon.commit()
    
class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        else:
            print ("Received event - %s, path - %s" %(event.event_type, event.src_path))
            if event.event_type == "modified" and os.path.exists(event.src_path):
                try:
                    fileName = Path(event.src_path).name
                    fileExt = Path(event.src_path).suffix.replace('.','')
                    fileSize = os.path.getsize(event.src_path)
                    fileCreateTime = datetime.fromtimestamp(os.path.getctime(event.src_path))
                    mlsec = datetime.now().strftime("%f")
                    fileArrivalTime = fileCreateTime.strftime('%Y-%m-%d %H:%M:%S:{}'.format(mlsec))
                    fileTimestamp = fileCreateTime.strftime("%Y%m%d%H%M%S{}".format(mlsec))
                    fileNameSplit = fileName.split('_')[-1]
                    
                    if len(fileNameSplit) == len(fileName):
                        fileSender = "DEFAULT"
                    else:
                        fileSender = fileNameSplit.split('.')[0]
                        
                    print("File name - %s" % fileName)
                    print("File arrival time - %s" % fileArrivalTime)
                    print("File size - %s" % fileSize)
                    print("File sender - %s" % fileSender)
                    
                    insertIncomingFileMetaData(fileName, fileArrivalTime, fileSize, fileSender)
                    moveFileName = g_pathArchive + "\\" + Path(event.src_path).stem + "_" + fileTimestamp + "." + fileExt
                
                    shutil.move(event.src_path, moveFileName)
                except Exception as ex:
                    print (ex)

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
       
    g_dbCon = sqlite3.connect(g_dbPath, check_same_thread=False)
    
    print ("File watcher has started to watch \"%s\" directory." % g_pathInbound)
        
    w = Watcher()
    w.run()