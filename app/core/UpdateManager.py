import os

import requests
import yaml

file_path_session = os.path.join('database', 'apscheduler.json')


class UpdateManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def update(self):
        yaml_url = "https://raw.githubusercontent.com/eslam2010011/CS-Tools/main/cs_tools.yaml"
        response = requests.get(yaml_url)
        remote_yaml_content = response.text
        remote_yaml_data = yaml.safe_load(remote_yaml_content)
        local_yaml_data = self.file_manager.read_data()
        if remote_yaml_data["version"] > local_yaml_data["version"]:
            print("A newer version is available.")
        else:
            print("You are up to date.")
