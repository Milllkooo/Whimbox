import cv2
import traceback
from whimbox.common.utils.asset_utils import *
from whimbox.common.cvars import *

class PosiTemplate(AssetBase):
    def __init__(self, name = None, posi=None, img_path=None, anchor=ANCHOR_TOP_LEFT, expand=False):
        """坐标管理类

        Args:
            posi (AnchorPosi, optional): 可选。若有，则使用该坐标. Defaults to None.
            img_path (str, optional): 可选。若有，则使用该图片。图片应符合bbg格式. Defaults to None.
            anchor (str, optional): 可选。锚点类型. Defaults to ANCHOR_TOP_LEFT.
            expand (bool, optional): 可选。是否在垂直方向上扩展. Defaults to False.
        """
        if name is None:
            super().__init__(get_name(traceback.extract_stack()[-2]))
        else:
            super().__init__(name)
        self.anchor = anchor
        self.position = None
        self.expand = expand
        
        if posi is None and img_path is None:
            img_path = self.get_img_path()

        if posi != None:
            self.position = posi
        else:
            image = cv2.imread(img_path)
            self.position = asset_get_bbox(image, anchor=self.anchor, expand=self.expand)


class Area(PosiTemplate):
    def __init__(self, name=None, anchor=ANCHOR_TOP_LEFT, expand=False):
        name = get_name(traceback.extract_stack()[-2])
        super().__init__(name, anchor=anchor, expand=expand)
    
    def center_position(self):
        return self.position.get_center()
    
    def click(self, target_box=None, offset=(0, 0)):
        self.position.click(target_box=target_box, offset=offset)
