import datetime
from utils.action_utils import ActionUtils


class CurrentTimeAction:
    @classmethod
    def get_response(cls, _input_str: str, main_str: str, error_str: str, _: ActionUtils, __: object) -> str:
        try:
            time: datetime.datetime = datetime.datetime.now()
            hour, minute = time.hour, time.minute
            return main_str.format(hour=hour, minutes=minute)
        except (Exception,) as e:
            print(e)
            return error_str
