from utils.action_helper.actions import current_time_action, greet_action, play_song_action, clear_chat_action, \
    tell_joke_action, repeat_action, open_website_action
from utils.config_helper import ConfigHelper
from utils.action_utils import ActionUtils, TriggerInfos
from utils.intent_classifier import Classifier
from utils.itf.itf import TokenDetector
from typing import *
import logging
import asyncio

from utils.plugin_manager import PluginManager


class BaxterPlugin:
    def __init__(self) -> None:
        self.name: str = 'untitled'
        self.version: float = 1.0

    @classmethod
    def get_response(cls, _input_str: str, _main_str: str, _error_str: str, _action_utils: ActionUtils,
                     _: TriggerInfos) -> str:
        return 'Default Response!'

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> float:
        return self.version


class ActionHelper:
    def __init__(self, config_helper: ConfigHelper, token_detector: TokenDetector, classifier: Classifier) -> None:
        self.__config_helper: ConfigHelper = config_helper
        self.__action_utils: ActionUtils = ActionUtils(config_helper=config_helper,
                                                       token_detector=token_detector,
                                                       action_helper=self,
                                                       classifier=classifier)
        self.__plugin_manager: PluginManager = PluginManager(classifier)

        self.__actions: dict = {
            'get_current_time': current_time_action.CurrentTimeAction(),
            'greet_user': greet_action.GreetAction(),
            'play_song': play_song_action.PlaySongAction(),
            'clear_chat': clear_chat_action.ClearChatAction(),
            'tell_joke': tell_joke_action.TellJokeAction(),
            'repeat': repeat_action.RepeatAction(),
            'open_website': open_website_action.OpenWebsiteAction(),
        }
        self.__actions.update(self.__plugin_manager.get_plugin_actions())
        self.__plugins: List[BaxterPlugin] = []

        from utils.ui.ui_helper import Ui  # import locally to avoid circular imports but still have type hints
        self.__ui: Union[Ui, None] = None

    def set_ui(self, ui) -> None:
        self.__action_utils.set_ui(ui)
        self.__ui = ui

    def get_plugin_manager(self) -> PluginManager:
        """
        Returns the Plugin Manager which is used to load plugins
        :return: PluginManager instance
        """
        return self.__plugin_manager

    def action_exists(self, action_key: str) -> bool:
        """
        :param action_key: string - action key also known as action name
        :return: bool - True if action exists, False if not
        """
        return action_key in self.__actions.keys()

    def try_action(self, input_str: str, action_key: str, main_str: str, error_str: str,
                   trigger_infos: TriggerInfos) -> Any:
        """
        :param input_str: string - input string of the user
        :param action_key: string - action key also known as action name
        :param main_str: string - main response string of action (randomly chosen from patterns list)
        :param error_str: string - error response string of action
        :param trigger_infos: TriggerInfos - util class to pass infos about the current trigger of an action
        :return: Any - response of action, should be a string
        """
        if action_key == 'stopword-detected':
            return None
        if action_key is None:
            return main_str
        action: Callable = self.__actions.get(action_key)
        if action is None:
            return main_str
        # return action(input_str, main_str, error_str, self.__action_utils)
        # every class linked in self.__actions MUST have a get_response method
        try:
            # return action.get_response(input_str, main_str, error_str, self.__action_utils,  # type: ignore
            #                            trigger_infos)
            # check if the get_response function is a coroutine (async function)
            if asyncio.iscoroutinefunction(action.get_response):
                return asyncio.run(action.get_response(input_str, main_str, error_str, self.__action_utils,
                                                       trigger_infos))
            else:
                return action.get_response(input_str, main_str, error_str, self.__action_utils,
                                           trigger_infos)
        except AttributeError:
            raise Exception(f'Action {action_key} has no get_response method')
        except Exception as e:
            logging.error(['[ActionHelper -> try_action]', 'While trying to execute action', action_key, e])
            return error_str
