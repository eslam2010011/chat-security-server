import os
import zipfile
from datetime import datetime

import firebase_admin
from apscheduler.schedulers.blocking import BlockingScheduler
from firebase_admin import credentials, storage


class BackupManager:
    def __init__(self, folder_paths, service_account_key_path, storage_bucket_url):
        self.folder_paths = folder_paths
        self.service_account_key_path = service_account_key_path
        self.storage_bucket_url = storage_bucket_url
        self.backup_folder_name = None
        self.backup_zip_name = None

    def setup_firebase(self):
        cred = credentials.Certificate(self.service_account_key_path)
        storage_app = firebase_admin.initialize_app(cred, {
            'storageBucket': self.storage_bucket_url
        })
        self.bucket = storage.bucket()

    def convert_folder_to_zip(self, folder_path, folder_name):
        self.backup_folder_name = datetime.now().strftime("%Y-%m-%d")
        self.backup_zip_name = f"{self.backup_folder_name + folder_name}.zip"
        zip_path = os.path.join(folder_path, self.backup_zip_name)
        print(zip_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

    def upload_to_firebase_storage(self, folder_path):
        blob_name = f"backups/{self.backup_zip_name}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(os.path.join(folder_path, self.backup_zip_name))

    def cleanup_local_backup(self, folder_path):
        os.remove(os.path.join(folder_path, self.backup_zip_name))

    def perform_backup(self):
        for folder_path in self.folder_paths:
            self.convert_folder_to_zip(folder_path,folder_path)
            self.upload_to_firebase_storage(folder_path)
            self.cleanup_local_backup(folder_path)

    def start_scheduler(self):
        self.setup_firebase()
        self.perform_backup()
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.perform_backup, 'cron', day='*', hour='0')
        # scheduler.start()
