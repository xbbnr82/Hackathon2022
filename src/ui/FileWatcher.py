import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys
from datetime import datetime
from pathlib import Path
import configparser
import pandas as pd
import shutil
from ddm.models import IncomingFileMetaData
import threading

g_pathInbound = "./data/inbound"
g_pathArchive = "./data/archive"

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
    
class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        else:
            print ("Received event - %s, path - %s" %(event.event_type, event.src_path))
            if event.event_type == "modified" and os.path.exists(event.src_path):
                fileName = Path(event.src_path).name
                fileExt = Path(event.src_path).suffix.replace('.','')
                fileSize = os.path.getsize(event.src_path)
                fileCreateTime = datetime.fromtimestamp(os.path.getctime(event.src_path))
                mlsec = datetime.now().strftime("%f")
                fileArrivalTime = fileCreateTime.strftime('%Y-%m-%d %H:%M:%S:{}'.format(mlsec))
                fileTimestamp = fileCreateTime.strftime("%Y%m%d%H%M%S{}".format(mlsec))
                fileNameSplit = fileName.split('_')[-1]
                #fileNoOfRecords = 0
                
                if len(fileNameSplit) == len(fileName):
                    fileSender = "DEFAULT"
                else:
                    fileSender = fileNameSplit.split('.')[0]
                incomingFileMetaData = IncomingFileMetaData()
                incomingFileMetaData.fileName = fileName
                incomingFileMetaData.arrivalTime = fileArrivalTime
                incomingFileMetaData.size = fileSize
                incomingFileMetaData.sender = fileSender
                incomingFileMetaData.save()
                moveFileName = g_pathArchive + "\\" + Path(event.src_path).stem + "_" + fileTimestamp + "." + fileExt
                shutil.move(event.src_path, moveFileName)

def FileWatcher():
    w = Watcher()
    w.run()

def start():
    t1 = threading.Thread(name='FileWatcher',target=FileWatcher)
    t1.start()
