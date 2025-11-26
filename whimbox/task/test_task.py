from whimbox.task.task_template import TaskTemplate, register_step
import time
from whimbox.common.logger import logger

class TestTask(TaskTemplate):
    def __init__(self):
        super().__init__("test_task")
        self.count = 0

    @register_step("测试步骤")
    def step1(self):
        while not self.need_stop():
            logger.info(f"测试步骤，第{self.count}次")
            self.count += 1
            time.sleep(5)

if __name__ == "__main__":
    import cv2
    from whimbox.common.path_lib import *
    from whimbox.interaction.interaction_core import itt
    from whimbox.common.utils.img_utils import *
    from whimbox.ui.ui_assets import *
    from whimbox.common.cvars import IMG_RATE
    # cap = cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763953735.083236.png"))
    # cap = crop(cap, IconBGSkipDialog.bbg_posi)
    # print(itt.get_img_existence(IconBGSkipDialog, cap=cap, ret_mode=IMG_RATE, show_res=True))
    while True:
        print(itt.get_img_existence(ButtonZxxyRewarded, ret_mode=IMG_RATE, show_res=True))
        time.sleep(0.5)