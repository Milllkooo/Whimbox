import cv2
import numpy as np
import traceback
from copy import deepcopy

from whimbox.common.timer_module import Timer
from whimbox.common.utils.asset_utils import *
from whimbox.common.cvars import *
from whimbox.common.utils.img_utils import crop, process_with_hsv_limit


class ImgIcon(AssetBase):
    
    def __init__(self,
                 path=None,
                 name=None,
                 is_bbg=None,
                 bbg_posi=None,
                 cap_posi = None,
                 threshold=None,
                 hsv_limit=None,
                 gray_limit=None,
                 win_text = None,
                 offset = 0,
                 print_log = LOG_ALL if DEBUG_MODE else LOG_WHEN_TRUE):
        """创建一个img对象，用于图片识别等。

        Args:
            path (str): 图片路径。
            name (str): 图片名称。默认为图片名。
            is_bbg (bool, optional): 是否为黑色背景图片. Defaults to True.
            bbg_posi (list/None, optional): 黑色背景的图片坐标，默认自动识别坐标. Defaults to None.
            cap_posi (list/str, optional): 截图坐标。注意：可以填入'bbg'字符串关键字，使用bbg坐标; 可以填入'all'字符串关键字，截图全屏. Defaults to None.
            threshold (float|tuple(float, float), optional): 匹配阈值. var1>var2. Defaults to 0.91.
            win_text (str, optional): 匹配时图片内应该包含的文字. Defaults to None.
            offset (int, optional): 截图范围偏移. Defaults to 0.
            print_log (int, optional): 打印日志模式. Defaults to LOG_NONE.
        """
        if name is None:
            super().__init__(get_name(traceback.extract_stack()[-2]))
        else:
            super().__init__(name)
        
        if path is None:
            path = self.get_img_path()

        if threshold is None:
            threshold = 0.98

        self.origin_path = path
        self.raw_image = cv2.imread(self.origin_path)
        if is_bbg == None:
            if self.raw_image.shape == (1080,1920,3):
                is_bbg = True
            else:
                is_bbg = False        
        self.is_bbg = is_bbg
        if self.is_bbg and bbg_posi is None:
            self.bbg_posi = asset_get_bbox(self.raw_image)
        else:
            self.bbg_posi = bbg_posi
        if cap_posi == 'bbg':
            self.cap_posi = self.bbg_posi
        elif cap_posi == None and is_bbg == True:
            self.cap_posi = self.bbg_posi
        elif cap_posi == 'all':
            self.cap_posi = [0, 0, 1920, 1080]
        else:
            self.cap_posi = cap_posi    
        
        if self.cap_posi == None:
            self.cap_posi = [0, 0, 1080, 1920]
        
        self.threshold = threshold
        self.hsv_limit = hsv_limit
        self.gray_limit = gray_limit
        self.win_text = win_text
        self.offset = offset
        self.print_log = print_log
            
        if self.offset != 0:
            self.cap_posi = list(np.array(self.cap_posi) + np.array([-self.offset, -self.offset, self.offset, self.offset]))
            
        self.cap_center_position_xy = [(self.cap_posi[0]+self.cap_posi[2])/2, (self.cap_posi[1]+self.cap_posi[3])/2]
        
        
        if self.is_bbg:
            self.image = crop(self.raw_image, self.bbg_posi)
        else:
            self.image = self.raw_image.copy()
        
        if self.hsv_limit is not None:
            temp_image = process_with_hsv_limit(self.image, self.hsv_limit[0], self.hsv_limit[1])
            box = asset_get_bbox(temp_image)
            self.image = crop(temp_image, box, copy=False)
        elif self.gray_limit is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGRA2GRAY)
            _, temp_image = cv2.threshold(self.image, self.gray_limit[0], self.gray_limit[1], cv2.THRESH_BINARY)
            box = asset_get_bbox(temp_image)
            self.image = crop(temp_image, box, copy=False)
            
    def copy(self):
        return deepcopy(self)
    
    def show_image(self):
        cv2.imshow('123', self.image)
        cv2.waitKey(0)


class GameImg(AssetBase):
    def __init__(self, path=None, name=None):
        if name is None:
            super().__init__(get_name(traceback.extract_stack()[-2]))
        else:
            super().__init__(name)
        
        if path is None:
            path = self.get_img_path()
    
        self.origin_path = path
        self.raw_image = cv2.imread(self.origin_path, cv2.IMREAD_UNCHANGED)
    
    def copy(self):
        return deepcopy(self)
    

if __name__ == '__main__':
    # img = refrom_img(cv2.imread("assets\\imgs\\common\\coming_out_by_space.jpg"),posi_manager.get_posi_from_str('coming_out_by_space'))
    # cv2.imwrite("assets\\imgs\\common\\coming_out_by_space.jpg", img)
    # get_img_from_imgname(COMING_OUT_BY_SPACE)
    # pname = F_BUTTON
    # p = auto_import_img("assets\\imgs\\common\\ui\\" + "time_menu_core" + ".jpg", "swimming")
    # print(p)
    pass
