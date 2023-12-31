from dataclasses import dataclass

import webview
from utils.config_helper import ConfigHelper
from utils.itf.itf import TokenDetector
from typing import *
import re


@dataclass
class TriggerInfos:
    # Util class to pass infos about the current trigger of an action
    ui: webview.Window
    last_action: Union[str, None]
    last_input: Union[str, None]


class ActionUtils:
    def __init__(self, config_helper: ConfigHelper, token_detector: TokenDetector, action_helper, classifier) -> None:
        self.__config_helper: ConfigHelper = config_helper
        self.__token_detector: TokenDetector = token_detector
        self.__action_helper = action_helper
        self.__classifier = classifier

        from utils.ui.ui_helper import Ui  # import locally to avoid circular imports but still have type hints
        self.__ui: Union[Ui, None] = None

    def set_ui(self, ui) -> None:
        self.__ui = ui

    def request_input(self, prompt: str, callback: Callable[[str], None]) -> None:
        """
        Use this method if you want to request some input from the user.
        :param prompt: str -> prompt to send to the ui (message to display)
        :param callback: Callable[[str], None] -> callback to call when the user sends a message
        :return: None
        """
        self.__ui.request_next_message(prompt, callback)

    async def request_input_async(self, prompt: str) -> str:
        """
        Use this method if you want to request some input from the user.
        :param prompt: str -> prompt to send to the ui (message to display)
        :return: str -> response from the user
        """
        return await self.__ui.request_next_message_async(prompt)

    def send_message(self, message: str) -> None:
        """
        This method sends a message to the ui
        :param message: str -> message to send
        :return: None
        """
        self.__ui.send_message(message)

    def get_classifier(self):
        return self.__classifier

    def get_action_helper(self):
        return self.__action_helper

    def get_config_helper(self) -> ConfigHelper:
        return self.__config_helper

    def get_token_detector(self) -> TokenDetector:
        return self.__token_detector

    @staticmethod
    def get_part_by_indexes(s: str, start_idx: int, end_idx: int) -> Union[str, None]:
        if start_idx < 0 or end_idx < 0:
            return None
        return ' '.join(s.split()[start_idx:end_idx + 1])

    def handle_if_statements(self, s: str) -> str:
        # check if %if_*% and %if_*_end% are in the string (* must be equal)
        if re.search(r'%if_(.*?)%', s) and re.search(r'%if_(.*?)_end%', s):
            # var name we have to check if exists is between %if_ and % (e.g. %if_name% -> name)
            var_name: str = re.search(r'%if_(.*?)%', s).group(1)
            # check if var_name if is closed
            if not re.search(r'%if_' + var_name + r'_end%', s):
                raise Exception(f'No closing tag found for {var_name}')

            # if var_name in config
            if not self.__config_helper.setting_exists(var_name):
                # var_name not found, if statement is false, cut off at start and append after end if no %else%
                # and %else_end% is in the string
                if not re.search(r'%else%', s) and not re.search(r'%else_end%', s):
                    start_idx_if: int = s.index(f'%if_{var_name}%')
                    end_idx_if: int = s.index(f'%if_{var_name}_end%') + len(f'%if_{var_name}_end%')
                    s: str = s[:start_idx_if] + s[end_idx_if:]
                    return s
                else:
                    # TODO: handle %else% and %else_end%
                    return s

            # the val we have to replace is between %if_*% and %if_*_end% (e.g. %if_name%, {name} %if_name_end% -> name)
            var_value_match = re.search(r'%if_.*?{([^{}]+)}.*?%if_.*?_end%', s)

            if not var_value_match:
                raise Exception('No value found for if statement')
            var_value_key: str = var_value_match.group(1)

            if not self.__config_helper.setting_exists(var_value_key):
                raise Exception(f'No value found for {var_value_key}')

            var_value: str = str(self.__config_helper.get_config_setting(var_value_key))

            s = s.replace(f'%if_{var_name}%', '')
            s = s.replace(f'%if_{var_name}_end%', '')
            s = s.replace(f'{{{var_value_key}}}', var_value)
        return s
