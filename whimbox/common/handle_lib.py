import psutil
import win32gui, win32process, win32con
from whimbox.common.cvars import PROCESS_NAME

def _get_handle():
    """获得游戏窗口句柄"""
    
    def get_hwnds_for_pid(pid):
        hwnds = []

        def callback(hwnd, hwnds):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            # 检查是否属于目标进程，且窗口是可见并且不是子窗口
            if found_pid == pid and win32gui.IsWindowVisible(hwnd) and win32gui.GetParent(hwnd) == 0:
                hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, hwnds)
        return hwnds
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == PROCESS_NAME:
            hwnds = get_hwnds_for_pid(proc.info['pid'])
            if hwnds:
                return hwnds[0]
    return 0

class handle_obj():
    def __init__(self) -> None:
        self.handle = _get_handle()

    def get_handle(self):
        return self.handle

    def refresh_handle(self):
        self.handle = _get_handle()
        
    def set_foreground(self):
        if self.handle:
            # 如果窗口被最小化，先恢复显示
            if win32gui.IsIconic(self.handle):
                win32gui.ShowWindow(self.handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.handle)
    
    def is_alive(self):
        if not self.handle:
            return False
        
        # 检查窗口句柄是否仍然有效
        if not win32gui.IsWindow(self.handle):
            return False
        
        return True

    def check_shape(self):
        if self.handle:
            _, _, width, height = win32gui.GetClientRect(self.handle)
            if height == 0:
                return False, 0, 0
            elif width/height == 1920/1080:
                if height < 1080 or height > 1440:
                    return False, width, height
                else:
                    return True, width, height
            else:
                return False, width, height
        return False, 0, 0
            

HANDLE_OBJ = handle_obj()

if __name__ == '__main__':
    pass
