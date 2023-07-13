import os
import zipfile


class FolderToZipConverter:
    def __init__(self, folder_path, zip_path):
        self.folder_path = folder_path
        self.zip_path = zip_path

    def convert(self):
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, self.folder_path))
