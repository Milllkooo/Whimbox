import threading
import time

from whimbox.common import timer_module
import numpy as np
from whimbox.common.handle_lib import HANDLE_OBJ
import win32ui
import cv2
import win32gui
import ctypes
from whimbox.common.logger import logger
from whimbox.common.cvars import DEBUG_MODE


class Capture():
    def __init__(self):
        self.capture_cache = np.zeros_like((1080,1920,3), dtype="uint8")
        self.resolution = None
        self.max_fps = 30
        self.fps_timer = timer_module.Timer(diff_start_time=1)
        self.capture_cache_lock = threading.Lock()
        self.capture_times = 0
        self.cap_per_sec = timer_module.CyclicCounter(limit=3).start()
        self.last_cap_times = 0

    def _cover_privacy(self, img: np.ndarray) -> np.ndarray:
        return img

    def _normalize_shape(self, img: np.ndarray) -> np.ndarray:
        if self._check_shape(img):
            self.resolution = img.shape[:2]
            if img.shape == (1080,1920,4):
                return img
            else:
                return cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_NEAREST)
        else:
            self.resolution = None
            return None
    
    def _get_capture(self) -> np.ndarray:
        """
        需要根据不同截图方法实现该函数。
        """
    
    def _check_shape(self, img:np.ndarray):
        if img is None:
            return False
        if img.shape == [1080,1920,4]:
            return True
        else:
            return False
        
    def capture(self, force=False) -> np.ndarray:
        """
        供外部调用的截图接口

        Args:
            force: 无视帧率限制，强制截图
        """
        if DEBUG_MODE:
            r = self.cap_per_sec.count_times()
            if r:
                if r != self.last_cap_times:
                    logger.trace(f"capps: {r/3}")
                    self.last_cap_times = r
                elif r >= 10*3:
                    logger.trace(f"capps: {r/3}")
                elif r >= 20*3:
                    logger.debug(f"capps: {r/3}")
                elif r >= 40*3:
                    logger.info(f"capps: {r/3}")
        self._capture(force)
        self.capture_cache_lock.acquire()
        cp = self.capture_cache.copy()
        self.capture_cache_lock.release()
        return cp
    
    def _capture(self, force) -> None:
        if (self.fps_timer.get_diff_time() >= 1/self.max_fps) or force:
            self.fps_timer.reset()
            self.capture_cache_lock.acquire()
            self.capture_times+=1
            while 1:
                normalized_img = self._normalize_shape(self._get_capture())
                if normalized_img is not None:
                    self.capture_cache = normalized_img
                    break
                else:
                    time.sleep(2)
            self.capture_cache_lock.release()
        else:
            pass
    
from ctypes.wintypes import RECT
import win32print, win32api

class BitbltCapture(Capture):
    """
    支持Windows10, Windows11的截图。（不支持无限暖暖）
    """
    GetDC = ctypes.windll.user32.GetDC
    CreateCompatibleDC = ctypes.windll.gdi32.CreateCompatibleDC
    GetClientRect = ctypes.windll.user32.GetClientRect
    CreateCompatibleBitmap = ctypes.windll.gdi32.CreateCompatibleBitmap
    SelectObject = ctypes.windll.gdi32.SelectObject
    BitBlt = ctypes.windll.gdi32.BitBlt
    SRCCOPY = 0x00CC0020
    GetBitmapBits = ctypes.windll.gdi32.GetBitmapBits
    DeleteObject = ctypes.windll.gdi32.DeleteObject
    ReleaseDC = ctypes.windll.user32.ReleaseDC
    GetDeviceCaps = win32print.GetDeviceCaps
    

    def __init__(self):
        super().__init__()
        self.max_fps = 30
        self.monitor_num = 1
        self.monitor_id = 0
        # self.scale_factor = self._get_screen_scale_factor()
        
    def _check_shape(self, img:np.ndarray):
        if img.shape == (1080,1920,4):
            return True
        else:
            HANDLE_OBJ.refresh_handle()
            logger.info("research handle: "+str(HANDLE_OBJ.get_handle()))
            if self.monitor_num>1:
                if self.monitor_id==(self.monitor_num-1):
                    self.monitor_id=0
                else:
                    self.monitor_id+=1
                logger.info("research monitor: "+str(self.monitor_id))
            return False
    
    def _get_screen_scale_factor(self):
        monitors = win32api.EnumDisplayMonitors()
        self.monitor_num = len(monitors)
        monitor = monitors[self.monitor_id][2]
        if self.monitor_num>1:
            logger.info("multiple monitor detected: "+str(self.monitor_num))
        # Get a pointer to a DEVICE_SCALE_FACTOR value
        scale_factor = ctypes.c_int()

        # Call the GetScaleFactorForMonitor function with the monitor handle and scale factor pointer
        ctypes.windll.shcore.GetScaleFactorForMonitor(ctypes.c_int(monitor), ctypes.byref(scale_factor))

        # Print the scale factor value
        return float(scale_factor.value/100)
    
    def _get_capture(self):
        r = RECT()
        self.GetClientRect(HANDLE_OBJ.get_handle(), ctypes.byref(r))
        width, height = r.right, r.bottom
        # left, top, right, bottom = win32gui.GetWindowRect(handle_lib.HANDLEOBJ.get_handle())
        # 获取桌面缩放比例
        #desktop_dc = self.GetDC(0)
        #scale_x = self.GetDeviceCaps(desktop_dc, 88)
        #scale_y = self.GetDeviceCaps(desktop_dc, 90)
        height=int(height)
        if height in list(map(int, [1080/0.75, 1080/1.25, 1080/1.5, 1080/1.75, 1080/2, 1080/2.25, 1080/2.5, 1080/2.75, 1080/3])):
            logger.warning_once("You seem to have monitor scaling set? It is automatically recognized and this does not affect usage.")
            logger.warning_once(f"scale: {height}")
            width = 1920
            height = 1080
            # 计算实际截屏区域大小
            # width = int(int(width)*self.scale_factor)
            # height = int(int(height)*self.scale_factor)
        
        # 开始截图
        dc = self.GetDC(HANDLE_OBJ.get_handle())
        cdc = self.CreateCompatibleDC(dc)
        bitmap = self.CreateCompatibleBitmap(dc, width, height)
        self.SelectObject(cdc, bitmap)
        # pt = time.time()
        self.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, self.SRCCOPY)
        # logger.trace(f'cap t: {time.time()-pt}')
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = width * height * 4
        buffer = bytearray(total_bytes)
        byte_array = ctypes.c_ubyte * total_bytes
        self.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        self.DeleteObject(bitmap)
        self.DeleteObject(cdc)
        self.ReleaseDC(HANDLE_OBJ.get_handle(), dc)
        # 返回截图数据为numpy.ndarray
        ret = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
        return ret
    
    def _cover_privacy(self, img) -> np.ndarray:
        img[1053 : 1075, 1770 : 1863, :3] = 128
        return img
    
class PrintWindowCapture(Capture):
    def __init__(self):
        super().__init__()
        self.max_fps = 30

    def _check_shape(self, img:np.ndarray):
        if img.shape[2] == 4 and img.shape[1]/img.shape[0] == 1920/1080:
            return True
        else:
            logger.info("游戏分辨率异常: "+str(img.shape))
            return False

    def _get_capture(self):
        hwnd = HANDLE_OBJ.get_handle()
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bottom - top

        hdc_window = win32gui.GetWindowDC(hwnd)
        hdc_mem = win32ui.CreateDCFromHandle(hdc_window)
        hdc_compat = hdc_mem.CreateCompatibleDC()

        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc_mem, width, height)
        hdc_compat.SelectObject(bmp)

        result = ctypes.windll.user32.PrintWindow(hwnd, hdc_compat.GetSafeHdc(), 3)

        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

        win32gui.DeleteObject(bmp.GetHandle())
        hdc_compat.DeleteDC()
        hdc_mem.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc_window)
        
        return img


if __name__ == '__main__':
    c = PrintWindowCapture()
    while 1:
        cv2.imshow("capture test", c.capture())
        cv2.waitKey(10)
        # time.sleep(0.01)
