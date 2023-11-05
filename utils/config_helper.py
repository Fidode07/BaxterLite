import os.path
import json
from typing import *


class ConfigHelper:
    def __init__(self, config_path: str = 'config.json') -> None:
        self.__config_path: str = config_path
        if not os.path.isfile(config_path):
            return
        self.__config_data: dict = self.__fetch_config()

    def __fetch_config(self) -> dict:
        return json.load(open(self.__config_path, 'r', encoding='utf-8'))

    def setting_exists(self, setting: str) -> bool:
        return setting in self.__config_data

    def get_config_setting(self, setting: str) -> Any:
        """
        This method returns the value of the setting specified in the parameter if it exists. If it doesn't exist, it
        returns None.
        :param setting: Key/name of the setting
        :return: Value of the setting (can also be None)
        """
        return self.__config_data.get(setting, None)

    def set_config_setting(self, setting: str, value: Union[str, int, None]) -> None:
        self.__config_data[setting] = value
        with open(self.__config_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.__config_data, indent=4, ensure_ascii=False))
