import pystray
import webview
from utils.ui.ui_helper import Ui
from PIL import Image


class TrayHelper:
    def __init__(self, ui: Ui) -> None:
        # Create a simple menu which contains "Open UI" and "Exit" options
        self.__menu = pystray.Menu(pystray.MenuItem('Open UI', self.__open_ui),
                                   pystray.MenuItem('Exit', self.__exit))
        # Create an icon
        self.__icon = self.get_icon_from_png('src/img/icon64.png')
        self.__ui_helper: Ui = ui

    @staticmethod
    def run_from_thread(ui: Ui) -> None:
        """
        :param ui: Ui -> UiHelper instance
        """
        tray_helper: TrayHelper = TrayHelper(ui)
        tray_helper.start()

    def start(self) -> None:
        """
        Start the tray icon
        """
        # Start the icon
        self.__icon.run()

    def __open_ui(self) -> None:
        self.__ui_helper.open_ui()

    def get_icon_from_png(self, path: str) -> pystray.Icon:
        """
        :param path: str -> path to the icon image
        :return: pystray.Icon -> icon
        """
        # use PIL to open the image and convert it to a format pystray can use
        image = Image.open(path)
        icon = pystray.Icon('name', menu=self.__menu, title='name')
        icon.icon = image
        return icon

    def __exit(self) -> None:
        """
        Exit the application
        """
        self.__icon.stop()
        self.__ui_helper.get_window().destroy()
        exit(0)
