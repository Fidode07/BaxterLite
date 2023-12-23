import asyncio

import webview

from utils.config_helper import ConfigHelper
from utils.intent_classifier import Classifier, Prediction
from utils.action_helper.action_helper import ActionHelper
from utils.action_utils import TriggerInfos
from typing import *


class Ui:
    def __init__(self, title: str, width: int, height: int, classifier: Classifier,
                 action_helper: ActionHelper, config_helper: ConfigHelper) -> None:
        """
        :param title: str -> title of the window
        :param width: int -> width of the window
        :param height: int -> height of the window
        :param classifier: Classifier -> classifier used to classify the user input
        :param action_helper: ActionHelper -> action helper passed to all actions get_response methods
        """
        self.__width: int = width
        self.__height: int = height
        self.__title: str = title

        self.__x, self.__y = self.__calculate_window_position()
        self.__window: webview.Window = webview.create_window(title, 'src/chat.html', width=width, height=height,
                                                              resizable=False, on_top=True, js_api=self, x=self.__x,
                                                              y=self.__y)

        self.__classifier: Classifier = classifier
        self.__action_helper: ActionHelper = action_helper
        self.__config_helper: ConfigHelper = config_helper

        self.__currently_ui_open: bool = False

        self.__window.events.shown += self.__on_window_shown
        self.__window.events.closing += self.__on_window_closed

        self.__last_action: Union[str, None] = None
        self.__last_input: Union[str, None] = None

        self.__callback: Union[Callable[[str], None], None] = None

    def close_current_ui(self) -> None:
        if self.__window:
            self.__window.destroy()
        self.__window = None

    def open_ui(self) -> None:
        # if the ui is already open
        if self.__currently_ui_open or self.__window:
            # make sure window is at correct position
            self.__on_window_shown()
            return
        if not self.__window and len(webview.windows) == 0:
            # create new window
            self.__window = webview.create_window(self.__title, 'src/chat.html', width=self.__width,
                                                  height=self.__height,
                                                  resizable=False, on_top=True, js_api=self, x=self.__x, y=self.__y)
            self.__window.events.shown += self.__on_window_shown
            self.__window.events.closing += self.__on_window_closed

    def __on_window_closed(self) -> None:
        self.__currently_ui_open = False
        self.__window = None

    def get_window(self) -> webview.Window:
        """
        :return: webview.Window -> returns the window
        """
        return self.__window

    def __build_last_trigger_data(self) -> TriggerInfos:
        return TriggerInfos(ui=self.__window, last_action=self.__last_action, last_input=self.__last_input)

    def prompt_response(self, response: str) -> None:
        """
        This method is called from the ui when the user sends a message and request_next_message was called before
        :param response: str -> response from the user
        :return: None
        """
        if not self.__callback:
            return
        self.__callback(response)
        self.__callback = None

    async def request_next_message_async(self, prompt: str) -> str:
        """
        Instead of saving the callback, we are waiting for the response and return it
        :param prompt: str -> prompt to send to the ui (message to display)
        :return: str -> response from the user
        """
        response: Union[str, None] = None

        def callback(r: str) -> None:
            nonlocal response
            response = r

        self.__callback = callback

        self.__window.evaluate_js(f'set_prompt(\'{prompt}\')')
        # Wait while callback is not called
        while not response:
            await asyncio.sleep(0.1)
        return response

    def send_message(self, message: str) -> None:
        """
        This method sends a message to the ui
        :param message: str -> message to send
        :return: None
        """
        self.__window.evaluate_js(f'pushMessage(\'{message}\', "ai")')  # -> It's a message from the AI

    def request_next_message(self, prompt: str, callback: Callable[[str], None]) -> None:
        """
        This method saves the callback and sends the prompt to the ui
        :param prompt: str -> prompt to send to the ui (message to display)
        :param callback: Callable[[str], None] -> callback to call when the user sends a message
        :return: None
        """
        self.__callback = callback
        self.__window.evaluate_js(f'set_prompt(\'{prompt}\')')

    def get_response(self, message: str) -> dict:
        """
        :param message: str -> message to classify
        :return: dict -> {'response': str} -> response to the message
        """
        try:
            classified: Prediction = self.__classifier.classify(message)
        except (Exception,):
            error_str: str = self.__config_helper.get_config_setting('classifier_error_str')
            if error_str:
                return {'response': error_str}
            return {'response': 'Sorry, I did not understand that. Maybe your input was too long.'}
        if len(webview.windows) > 0:
            self.__window = webview.windows[0]
        result: str = self.__action_helper.try_action(message,
                                                      classified.action,
                                                      classified.main_str,
                                                      classified.error_str,
                                                      self.__build_last_trigger_data())
        self.__last_input = message
        if self.__action_helper.action_exists(classified.action):
            if not classified.action == 'repeat':
                self.__last_action = classified.action
        else:
            self.__last_action = None

        return {'response': result if result else None}

    def __calculate_window_position(self) -> tuple:
        screen: tuple = tuple([int(val) for val in str(webview.screens[0])[:-1][1:].split(', ')])
        screen_width: int = screen[0]
        screen_height: int = screen[1]

        window_width: int = self.__width
        window_height: int = self.__height

        x: int = screen_width - window_width
        y: int = screen_height - window_height

        return x, y

    def __move_window_to_bottom_right(self, window: webview.Window) -> None:
        x, y = self.__calculate_window_position()
        window.move(x, y)

    def __on_window_shown(self) -> None:
        if not self.__window:
            return

        self.__currently_ui_open = True
        self.__move_window_to_bottom_right(self.__window)
        self.__window.evaluate_js(
            f'set_plugin_counter(\'{len(self.__action_helper.get_plugin_manager().get_plugin_actions())}\')')
