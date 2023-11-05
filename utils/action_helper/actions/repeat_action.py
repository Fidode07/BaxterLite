from utils.action_utils import ActionUtils, TriggerInfos
from utils.intent_classifier import Intent


class RepeatAction:
    @classmethod
    def get_response(cls, inp_str: str, main_str: str, error_str: str, action_utils: ActionUtils,
                     trigger_infos: TriggerInfos) -> str:
        try:
            blacklisted_actions: list = [None, 'repeat', 'stopword-detected']
            if trigger_infos.last_action in blacklisted_actions:
                print('Last action is blacklisted')
                return error_str
            # rerun last action
            new_trigger_infos: TriggerInfos = TriggerInfos(ui=trigger_infos.ui, last_action='repeat',
                                                           last_input=trigger_infos.last_input)
            intent_data: Intent = action_utils.get_classifier().get_intent_by_action(trigger_infos.last_action)
            if intent_data is None:
                print('No intent data found for last action')
                return error_str
            response: str = action_utils.get_action_helper().try_action(trigger_infos.last_input,
                                                                        trigger_infos.last_action,
                                                                        intent_data.main_str,
                                                                        intent_data.error_str,
                                                                        new_trigger_infos)
            if response is None:
                print('No response from last action')
                return error_str
            return main_str.format(response=response)
        except (Exception,) as e:
            print(e)
            return error_str
