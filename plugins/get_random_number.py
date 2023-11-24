from utils.action_helper.action_helper import BaxterPlugin
from utils.action_utils import ActionUtils, TriggerInfos
import random


class Plugin(BaxterPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = 'get_random_number'

    @classmethod
    def get_response(cls, _input_str: str, main_str: str, error_str: str, _action_utils: ActionUtils,
                     _: TriggerInfos) -> str:
        try:
            return main_str.format(number=random.randint(0, 99999))
        except (Exception,):
            return error_str
