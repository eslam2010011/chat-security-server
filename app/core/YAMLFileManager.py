import yaml


class YAMLFileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def write_data(self, data):
        with open(self.file_path, 'w') as file:
            yaml.dump(data, file)

    def read_data(self):
        with open(self.file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def edit_data(self, key_path, new_value):
        data = self.read_data()
        keys = key_path.split('.')
        current = data
        for key in keys[:-1]:
            current = current[key]
        current[keys[-1]] = new_value
        self.write_data(data)

    def delete_data(self, key_path):
        data = self.read_data()
        keys = key_path.split('.')
        current = data
        for key in keys[:-1]:
            current = current[key]
        del current[keys[-1]]
        self.write_data(data)

    def search_data(self, key_path):
        data = self.read_data()
        keys = key_path.split('.')
        current = data
        for key in keys[:-1]:
            current = current[key]
        return current[keys[-1]] if keys[-1] in current else None

    def search_key_value(self, key, value):
        data = self.read_data()
        results = []
        self._recursive_search_key_value(data, key, value, results)
        return results

    def search_key_value_autocomplete(self, value):
        data = self.read_data()
        results = []
        self._recursive_search_by_name_auto(data, value, results)
        return results

    def _recursive_search_by_name_auto(self, data, tool_name, results):
        if isinstance(data, dict):
            if 'name' in data and data['name'].lower().startswith(tool_name.lower()):
                results.append(data)
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._recursive_search_by_name_auto(value, tool_name, results)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._recursive_search_by_name_auto(item, tool_name, results)

    def _recursive_search_key_value(self, data, search_key, search_value, results):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == search_key and value == search_value:
                    results.append(data)
                if isinstance(value, (dict, list)):
                    self._recursive_search_key_value(value, search_key, search_value, results)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._recursive_search_key_value(item, search_key, search_value, results)

    def search_file(self, file_name):
        data = self.read_data()
        results = []
        self._recursive_search_file(data, file_name, results)
        return results

    def _recursive_search_file(self, data, file_name, results):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'file' and value == file_name:
                    results.append(data)
                if isinstance(value, (dict, list)):
                    self._recursive_search_file(value, file_name, results)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._recursive_search_file(item, file_name, results)

    def search_name_tools(self, tool_name):
        data = self.read_data()
        results = []
        self._recursive_search_name_tools(data, tool_name, results)
        return results

    def _recursive_search_name_tools(self, data, tool_name, results):
        if isinstance(data, dict):
            if ('name' in data and data['name'] == tool_name) or ('name' in data and data['name'] in tool_name):
                results.append(data)
            if 'category' in data and data['category'] == tool_name:
                results.append(data)
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._recursive_search_name_tools(value, tool_name, results)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._recursive_search_name_tools(item, tool_name, results)
