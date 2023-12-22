from utils.action_helper.action_helper import BaxterPlugin
from utils.action_utils import ActionUtils, TriggerInfos
import random


class Plugin(BaxterPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = 'get_random_number'

    @classmethod
    async def __fetch_number(cls, prompt: str, action_utils: ActionUtils) -> int:
        n: str = await action_utils.request_input_async(prompt)
        while not n.lstrip('-').isdigit():
            n = await action_utils.request_input_async('Bitte gib eine Zahl ein! (z.B. 1)')
        return int(n)

    @classmethod
    async def get_response(cls, _input_str: str, main_str: str, error_str: str, action_utils: ActionUtils,
                           _: TriggerInfos) -> str:
        try:
            smallest_number: int = await cls.__fetch_number(
                'Bitte nenne mir den kleinsten Wert, den die Zahl haben darf.', action_utils)
            biggest_number: int = await cls.__fetch_number('Wie groß darf die Zahl maximal sein?', action_utils)

            if smallest_number == biggest_number:
                return main_str.format(number=smallest_number)  # only one number possible

            if smallest_number > biggest_number:
                biggest_number, smallest_number = smallest_number, biggest_number

            return main_str.format(number=random.randint(smallest_number, biggest_number))
        except (Exception,):
            return error_str
