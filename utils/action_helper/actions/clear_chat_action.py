import logging
from utils.action_utils import ActionUtils, TriggerInfos


class ClearChatAction:
    @classmethod
    def get_response(cls, _: str, main_str: str, error_str: str, __: ActionUtils,
                     trigger_infos: TriggerInfos) -> str:
        try:
            trigger_infos.ui.evaluate_js('clear_chat()')
            return main_str
        except (Exception,) as e:
            logging.error(['[ClearChatAction -> get_response]', e])
            return error_str
