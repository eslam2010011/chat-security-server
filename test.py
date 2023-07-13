import os
from app.core.BackupManager import BackupManager
file_path = os.path.join('database')
file_path_resources = os.path.join('resources')
file_path_scripts = os.path.join('scripts')
file_path_cs_tools = os.path.join('scripts', '.json')
s = BackupManager([file_path, file_path_resources, file_path_scripts], file_path_cs_tools, ".appspot.com")
s.start_scheduler()

