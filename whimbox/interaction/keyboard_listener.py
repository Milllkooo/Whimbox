'''键盘状态记录器，暂不使用'''

from pynput import keyboard
import time
from typing import Dict

key_dict = {
    keyboard.Key.space: 'space',
    keyboard.KeyCode.from_char('f'): 'f',
    keyboard.KeyCode.from_char('w'): 'w',
}

class KeyStatus:
    def __init__(self):
        self.pressed = False
        self.last_press_time = None

class NikkiKeyboardListener: 
    def __init__(self):
        self.key_status: Dict[str, KeyStatus] = {}
        
        # 初始化每个按键的状态
        for key_str in key_dict.items():
            self.key_status[key_str] = KeyStatus()

        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)


    def record_key_down(self, key_str):
        if not self.key_status[key_str].pressed:
            self.key_status[key_str].pressed = True
            self.key_status[key_str].last_press_time = time.time()

    def record_key_up(self, key_str):
        self.key_status[key_str].pressed = False
        self.key_status[key_str].last_press_time = time.time()

    def _on_press(self, key):
        if key in key_dict:
            key_str = key_dict[key]
            self.record_key_down(key_str)

    def _on_release(self, key):
        if key in key_dict:
            key_str = key_dict[key]
            self.record_key_up(key_str)

    def get_key_status(self, key_str):
        """
        返回 (是否按下, 距离上次按下的时间间隔秒)
        如果处于按下状态，返回从第一次按下开始的间隔
        """
        if key_str not in self.key_status:
            raise ValueError(f"Key {key_str} not being tracked.")

        status = self.key_status[key_str]
        if status.last_press_time is None:
            return False, None
        
        return status.pressed, time.time() - status.last_press_time

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()