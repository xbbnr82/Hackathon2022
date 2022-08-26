import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys
from datetime import datetime
from pathlib import Path
import configparser

g_pathInbound = ""
g_pathArchive = ""

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
            print("File Name - %s" % Path(event.src_path).stem)
            print("File Name - %s" % Path(event.src_path).suffix.replace('.',''))
            if os.path.exists(event.src_path):
                print("File size - %s" % os.path.getsize(event.src_path))
                print("File create time - %s" % datetime.fromtimestamp(os.path.getctime(event.src_path)).strftime('%Y-%m-%d %H:%M:%S'))
                print("File modified time - %s" % datetime.fromtimestamp(os.path.getmtime(event.src_path)).strftime('%Y-%m-%d %H:%M:%S'))



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
        
    w = Watcher()
    w.run()
