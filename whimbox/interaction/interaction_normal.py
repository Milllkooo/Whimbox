import time
import ctypes
import win32api, win32con, win32gui

from whimbox.interaction.interaction_template import InteractionTemplate
from whimbox.interaction.vkcode import VK_CODE
from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.common.logger import logger
from whimbox.common.base_threading import ProcessThreading

class InteractionNormal(InteractionTemplate):

    def __init__(self):
        self.WM_MOUSEMOVE = 0x0200
        self.WM_LBUTTONDOWN = 0x0201
        self.WM_LBUTTONUP = 0x202
        self.WM_MOUSEWHEEL = 0x020A
        self.WM_RBUTTONDOWN = 0x0204
        self.WM_RBUTTONDBLCLK = 0x0206
        self.WM_RBUTTONUP = 0x0205
        self.WM_KEYDOWN = 0x100
        self.WM_KEYUP = 0x101
        self.GetDC = ctypes.windll.user32.GetDC
        self.CreateCompatibleDC = ctypes.windll.gdi32.CreateCompatibleDC
        self.GetClientRect = ctypes.windll.user32.GetClientRect
        self.CreateCompatibleBitmap = ctypes.windll.gdi32.CreateCompatibleBitmap
        self.SelectObject = ctypes.windll.gdi32.SelectObject
        self.BitBlt = ctypes.windll.gdi32.BitBlt
        self.SRCCOPY = 0x00CC0020
        self.GetBitmapBits = ctypes.windll.gdi32.GetBitmapBits
        self.DeleteObject = ctypes.windll.gdi32.DeleteObject
        self.ReleaseDC = ctypes.windll.user32.ReleaseDC
        self.VK_CODE = VK_CODE
        self.PostMessageW = ctypes.windll.user32.PostMessageW
        self.MapVirtualKeyW = ctypes.windll.user32.MapVirtualKeyW
        self.VkKeyScanA = ctypes.windll.user32.VkKeyScanA
        self.WHEEL_DELTA = 120
        
    def left_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def left_down(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        # time.sleep(0.01)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    
    def left_up(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        # time.sleep(0.01)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    def left_double_click(self):
        self.left_click()
        time.sleep(0.05)
        self.left_click()
    
    def right_down(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        # time.sleep(0.01)
        # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)

    def right_up(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        # time.sleep(0.01)
        # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def right_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    
    def middle_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
    
    def middle_scroll(self, distance):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, distance*self.WHEEL_DELTA, 0)

    def key_down(self, key):
        vk_code = self.get_virtual_keycode(key)
        win32api.keybd_event(vk_code, 0, 0, 0)
    
    def key_up(self, key):
        vk_code = self.get_virtual_keycode(key)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def key_press(self, key):
        self.key_down(key)
        time.sleep(0.05)
        self.key_up(key)
    
    def move_to(self, x: int, y: int, relative=False, isBorderlessWindow=False):
        x = int(x)
        y = int(y)

        if relative:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y)
        else:
            # wx, wy, w, h = win32gui.GetWindowRect(HANDLE_OBJ.get_handle())
            # if isBorderlessWindow:
            #     x += wx
            #     y += wy
            # else:
            #     x = x + wx + 11
            #     y = y + wy + 44
            # abs_x = int(x * 65536 / win32api.GetSystemMetrics(win32con.SM_CXSCREEN))
            # abs_y = int(y * 65536 / win32api.GetSystemMetrics(win32con.SM_CYSCREEN))
            # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE|win32con.MOUSEEVENTF_ABSOLUTE, abs_x, abs_y)
            screen_x, screen_y = win32gui.ClientToScreen(HANDLE_OBJ.get_handle(), (x, y))
            win32api.SetCursorPos((screen_x, screen_y))

KEY_DOWN = 'KeyDown'
KEY_UP = 'KeyUp'

class Operation():

    def __str__(self):
        return f'Operation: {self.key} {self.type}'
    def __init__(self, key:str, type, operation_start=time.time(), operation_end = time.time()):
        self.key = key
        self.type = type
        self.operation_start = operation_start
        self.operation_end = operation_end
        self.operated = False


if __name__ == '__main__':
    if True:
        time.sleep(1)
        print('start test')
        itn = InteractionNormal()
        itn.move_to(1028, 150)
        # while 1:
        #     time.sleep(1)
        #     itn.left_click()
    