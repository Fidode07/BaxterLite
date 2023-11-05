import logging
from utils.action_utils import ActionUtils


class GreetAction:
    @classmethod
    def get_response(cls, _: str, main_str: str, error_str: str, action_utils: ActionUtils, __: object) -> str:
        try:
            result: str = action_utils.handle_if_statements(main_str)
            return result
        except (Exception,) as e:
            logging.error(e)
            return error_str
