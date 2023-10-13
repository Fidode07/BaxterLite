from utils.action_helper.actions import fightclub_action, current_time_action, greet_action, play_song_action
from utils.config_helper import ConfigHelper
from utils.action_utils import ActionUtils
from utils.itf.itf import TokenDetector
from typing import *
import logging


class ActionHelper:
    def __init__(self, config_helper: ConfigHelper, token_detector: TokenDetector) -> None:
        self.__config_helper: ConfigHelper = config_helper
        self.__action_utils: ActionUtils = ActionUtils(config_helper=config_helper,
                                                       token_detector=token_detector)

        self.__actions: dict = {
            'check_fightclub_room2': fightclub_action.FightclubAction(),
            'get_current_time': current_time_action.CurrentTimeAction(),
            'greet_user': greet_action.GreetAction(),
            'play_song': play_song_action.PlaySongAction(),
            'stopword-detected': lambda m, e: None,
        }

    def try_action(self, input_str: str, action_key: str, main_str: str, error_str: str) -> str:
        if action_key is None:
            return main_str
        action: Callable = self.__actions.get(action_key)
        if action is None:
            return main_str
        # return action(input_str, main_str, error_str, self.__action_utils)
        # every class linked in self.__actions MUST have a get_response method
        try:
            return action.get_response(input_str, main_str, error_str, self.__action_utils)  # noqa
        except AttributeError:
            if action_key == 'stopword-detected':
                return ''
            raise Exception(f'Action {action_key} has no get_response method')
        except Exception as e:
            logging.error(['[ActionHelper -> try_action]', 'While trying to execute action', action_key, e])
            return error_str
