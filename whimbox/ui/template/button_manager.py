import numpy as np
import traceback

from whimbox.ui.template.img_manager import ImgIcon
from whimbox.common.utils.asset_utils import *
from whimbox.common.cvars import *


class Button(ImgIcon):
    def __init__(self, 
            path=None, 
            name=None,
            is_bbg = True , 
            threshold=None, 
            print_log = LOG_NONE, 
            cap_posi=None, 
            click_offset=None,
            hsv_limit=None,
            gray_limit=None,
            anchor=ANCHOR_TOP_LEFT):
        if name is None:
            name = get_name(traceback.extract_stack()[-2])
        super().__init__(path=path, name=name, is_bbg=is_bbg, threshold=threshold, 
            print_log=print_log, cap_posi=cap_posi, hsv_limit=hsv_limit, gray_limit=gray_limit, anchor=anchor)
        if click_offset is None:
            self.click_offset=np.array([0,0])
        else:
            self.click_offset=np.array(click_offset)
        if self.is_bbg:
            self.center_point = self.bbg_posi.get_center()
    
    
    # def click_position(self):
    #     # 在一个范围内随机生成点击位置 还没写
    #     return [int(self.center_point[0])+self.click_offset[0], int(self.center_point[1])+self.click_offset[1]]

    def click(self):
        self.cap_posi.click(offset=self.click_offset)

if __name__ == '__main__':
    pass # button_ui_cancel.show_image()
# print()