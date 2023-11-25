import pystray

from utils.config_helper import ConfigHelper
from utils.ui.ui_helper import Ui
from PIL import Image


class TrayHelper:
    def __init__(self, ui: Ui, config_helper: ConfigHelper) -> None:
        # Create a simple menu which contains "Open UI" and "Exit" options
        self.__menu = pystray.Menu(pystray.MenuItem('Open UI', self.__open_ui),
                                   pystray.MenuItem('Exit', self.__exit))
        # Create an icon
        self.__ui_helper: Ui = ui
        self.__config_helper: ConfigHelper = config_helper
        self.__icon = self.get_icon_from_png('src/img/icon1080.png')

    @staticmethod
    def run_from_thread(ui: Ui, config_helper: ConfigHelper) -> None:
        """
        :param ui: Ui -> UiHelper instance
        :param config_helper: ConfigHelper -> ConfigHelper instance
        :return: None
        """
        tray_helper: TrayHelper = TrayHelper(ui, config_helper)
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

        icon_name: str = self.__config_helper.get_config_setting('tray_icon_name')
        if not icon_name:
            icon_name = 'BaxterLite'  # default icon name
        icon = pystray.Icon(icon_name, menu=self.__menu, title=icon_name)
        icon.icon = image
        return icon

    def __exit(self) -> None:
        """
        Exit the application
        """
        self.__icon.stop()
        self.__ui_helper.get_window().destroy()
        exit(0)
