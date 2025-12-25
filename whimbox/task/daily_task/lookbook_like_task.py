"""
星绘图册点赞
"""

from whimbox.task.task_template import *
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.common.utils.ui_utils import *

class LookbookLikeTask(TaskTemplate):
    def __init__(self):
        super().__init__("lookbook_like_task")

    @register_step("打开星绘图册")
    def step1(self):
        ui_control.goto_page(page_esc)
        if not scroll_find_click(AreaEscEntrances, "星绘图册"):
            raise Exception("星绘图册入口未找到")
        itt.wait_until_stable(threshold=0.95)
    
    @register_step("随机点赞")
    def step2(self):
        if scroll_find_click(AreaXhsgBooklookWaterfall, IconXhsgBooklookLikeButton):
            itt.move_to((100, 100))
            itt.delay(1, comment="点赞移开鼠标看看")
            return
        else:
            raise Exception("点赞按钮未找到")
    
    @register_step("退出星绘图册")
    def step3(self):
        back_to_page_main()

if __name__ == "__main__":
    lookbook_like_task = LookbookLikeTask()
    lookbook_like_task.task_run()