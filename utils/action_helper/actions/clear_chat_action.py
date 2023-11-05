from utils.action_utils import ActionUtils
import webview


class ClearChatAction:
    @classmethod
    def get_response(cls, _: str, main_str: str, error_str: str, __: ActionUtils,
                     ui_window: webview.Window) -> str:
        try:
            ui_window.evaluate_js('clear_chat()')
            return main_str
        except (Exception,):
            return error_str
