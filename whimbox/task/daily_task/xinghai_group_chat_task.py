from whimbox.common.utils.ui_utils import wait_until_appear
from whimbox.task.task_template import *
from whimbox.interaction.interaction_core import itt
from whimbox.task.navigation_task.auto_path_task import AutoPathTask
from whimbox.common.keybind import keybind
from whimbox.ui.ui import ui_control
from whimbox.ui.ui_assets import *
from whimbox.ui.page_assets import *

class XinghaiGroupChatTask(TaskTemplate):
    def __init__(self):
        super().__init__("xinghai_group_chat_task")

    @register_step("前往星海沙发")
    def step1(self):
        task = AutoPathTask(path_name="星海拾光_聚会聊天")
        task_result = task.task_run()
        if task_result.status == STATE_TYPE_SUCCESS:
            return
        else:
            self.update_task_result(status=STATE_TYPE_STOP, message=task_result.message)
            return STEP_NAME_FINISH
    
    @register_step("进入群聊")
    def step2(self):
        if not wait_until_appear(IconSetdownFeature, area=AreaPickup):
            raise Exception("未找到坐下按钮")
        itt.key_press(keybind.KEYBIND_INTERACTION)
        itt.delay(2, comment="等待完全坐下")
        retry_time = 2
        while not self.need_stop() and retry_time > 0:
            ui_control.goto_page(page_chat)
            if not itt.get_img_existence(IconXhsgGroupChatFeature):
                ui_control.goto_page(page_main)
                retry_time -= 1
            else:
                break
        if retry_time == 0:
            self.update_task_result(status=STATE_TYPE_STOP, message="未能成功进入群聊")
            return STEP_NAME_FINISH
    
    @register_step("开始聊天")
    def step3(self):
        itt.key_press('1')
        time.sleep(0.5)
        itt.key_press('enter')
        time.sleep(0.5)
        ui_control.goto_page(page_main)
    
if __name__ == "__main__":
    task = XinghaiGroupChatTask()
    task.task_run()
