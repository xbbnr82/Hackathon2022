from django.apps import AppConfig
import os


class DdmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ddm'
    def ready(self):
        run_once = os.environ.get('Sart_File_Watcher') 
        if run_once is not None:
            return
        import FileWatcher
        FileWatcher.start()
        import AlertProcessor
        AlertProcessor.start()
        os.environ['Sart_File_Watcher'] = 'True' 



