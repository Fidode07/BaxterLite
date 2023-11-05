import webview
from utils.intent_classifier import Classifier, Prediction
from utils.action_helper.action_helper import ActionHelper
from utils.action_utils import TriggerInfos
from typing import *


class Ui:
    def __init__(self, title: str, width: int, height: int, classifier: Classifier,
                 action_helper: ActionHelper) -> None:
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

        x, y = self.__calculate_window_position()
        self.__window: webview.Window = webview.create_window(title, 'src/chat.html', width=width, height=height,
                                                              resizable=False, on_top=True, js_api=self, x=x, y=y)

        self.__classifier: Classifier = classifier
        self.__action_helper: ActionHelper = action_helper
        self.__currently_ui_open: bool = False

        self.__window.events.shown += self.__on_window_shown
        self.__window.events.closing += self.__on_window_closed

        self.__last_action: Union[str, None] = None

    def open_ui(self) -> None:
        # if the ui is already open
        if self.__currently_ui_open:
            # make sure window is at correct position
            self.__on_window_shown()
            return
        # if the ui is not open
        x, y = self.__calculate_window_position()
        ui: webview.Window = webview.create_window(self.__title, 'src/chat.html', width=self.__width,
                                                   height=self.__height, resizable=False, on_top=True, js_api=self,
                                                   x=x, y=y)
        ui.events.shown += self.__on_window_shown
        ui.events.closing += self.__on_window_closed
        self.__window = ui

    def __on_window_closed(self) -> None:
        self.__currently_ui_open = False
        self.__window = None

    def get_window(self) -> webview.Window:
        """
        :return: webview.Window -> returns the window
        """
        return self.__window

    def __build_last_trigger_data(self) -> TriggerInfos:
        return TriggerInfos(ui=self.__window, last_action=self.__last_action)

    def get_response(self, message: str) -> dict:
        """
        :param message: str -> message to classify
        :return: dict -> {'response': str} -> response to the message
        """
        classified: Prediction = self.__classifier.classify(message)

        result: str = self.__action_helper.try_action(message,
                                                      classified.action,
                                                      classified.main_str,
                                                      classified.error_str,
                                                      self.__build_last_trigger_data())
        if self.__action_helper.action_exists(classified.action):
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
        self.__currently_ui_open = True
        self.__move_window_to_bottom_right(self.__window)
