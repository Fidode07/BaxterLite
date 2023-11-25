import ctypes
from ctypes import wintypes
from collections import namedtuple
import atexit
from utils.ui.ui_helper import Ui


class KeyEvents(namedtuple("KeyEvents", ['event_type', 'key_code', 'scan_code', 'alt_pressed', 'time'])):
    pass


class HookEventHandler:
    def __init__(self, ui: Ui) -> None:
        self.__is_shift_pressed: bool = False
        self.__is_ctrl_pressed: bool = False

        self.__shortcut_key: str = '206158430274'
        self.__shift_key: str = '180388626592'
        self.__ctrl_key: str = '124554051746'

        self.__ui = ui

    def get_shortcut_key(self) -> str:
        return self.__shortcut_key

    def __is_shift(self, event: KeyEvents) -> bool:
        return event.key_code == int(self.__shift_key)

    def __is_ctrl(self, event: KeyEvents) -> bool:
        return event.key_code == int(self.__ctrl_key)

    def __is_shortcut(self, event: KeyEvents) -> bool:
        return event.key_code == int(self.__shortcut_key)

    def handle(self, event: KeyEvents) -> None:
        if self.__is_shift(event):
            self.__is_shift_pressed = event.event_type == 'key down'
        elif self.__is_ctrl(event):
            self.__is_ctrl_pressed = event.event_type == 'key down'
        elif all([self.__is_shortcut(event), self.__is_shift_pressed, self.__is_ctrl_pressed,
                  event.event_type == 'key down']):
            # Shortcut pressed
            self.__ui.open_ui()


class KeyboardListener:
    def __init__(self, hook_handler: HookEventHandler):
        self.handlers = []
        self.hook_id = None
        self.__shortcut_key = hook_handler.get_shortcut_key()
        self.__hook_handler = hook_handler

    def add_handler(self, handler):
        self.handlers.append(handler)

    def remove_handler(self, handler):
        self.handlers.remove(handler)

    def _low_level_handler(self, n_code, w_param, l_param):
        event_types = {0x100: 'key down', 0x101: 'key up', 0x104: 'key down', 0x105: 'key up'}
        event = KeyEvents(event_types[w_param], l_param[0], l_param[1], l_param[2] == 32, l_param[3])
        if event.key_code == int(self.__shortcut_key):
            self.__hook_handler.handle(event)
            # Cancel event
            return 1
        for h in self.handlers:
            h(event)
        return ctypes.windll.user32.CallNextHookEx(self.hook_id, n_code, w_param, l_param)

    def start_listening(self):
        cmpfunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        pointer = cmpfunc(self._low_level_handler)
        ctypes.windll.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        ctypes.windll.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        ctypes.windll.user32.SetWindowsHookExA.argtypes = (
            ctypes.c_int, wintypes.HANDLE, wintypes.HMODULE, wintypes.DWORD)
        self.hook_id = ctypes.windll.user32.SetWindowsHookExA(0x00D, pointer,
                                                              ctypes.windll.kernel32.GetModuleHandleW(None), 0)
        atexit.register(ctypes.windll.user32.UnhookWindowsHookEx, self.hook_id)
        while True:
            msg = ctypes.windll.user32.GetMessageW(None, 0, 0, 0)
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))


def thread_helper(ui: Ui):
    hook_handler = HookEventHandler(ui=ui)
    listener = KeyboardListener(hook_handler=hook_handler)
    listener.add_handler(hook_handler.handle)
    listener.start_listening()
