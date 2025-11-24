'''领取大月卡奖励'''
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
import time
from whimbox.common.utils.ui_utils import *
from whimbox.common.keybind import keybind

class MonthlyPassTask(TaskTemplate):
    def __init__(self):
        super().__init__("monthly_pass_task")

    @register_step("打开奇迹之旅")
    def step1(self):
        ui_control.goto_page(page_monthly_pass)
    
    @register_step("领取奖励")
    def step2(self):
        if wait_until_appear_then_click(ButtonMonthlyPassTab2):
            if wait_until_appear_then_click(ButtonMonthlyPassAward):
                if wait_until_appear(IconClickSkip, retry_time=2):
                    itt.delay(1, comment="不加延迟，有些电脑就是不行")
                    itt.wait_until_stable(threshold=0.95, timeout=2)
                    itt.key_press(keybind.KEYBIND_INTERACTION)
            time.sleep(0.5)
            if wait_until_appear_then_click(ButtonMonthlyPassTab1):
                if wait_until_appear_then_click(ButtonMonthlyPassAward):
                    if wait_until_appear(IconClickSkip):
                        itt.delay(1, comment="不加延迟，有些电脑就是不行")
                        itt.wait_until_stable(threshold=0.95, timeout=2)
                        itt.key_press(keybind.KEYBIND_INTERACTION)
                        self.update_task_result(message="成功领取奇迹之旅奖励")
                    return
        self.update_task_result(message="奇迹之旅无奖励可领取")
        
    @register_step("退出奇迹之旅")
    def step3(self):
        ui_control.goto_page(page_main)

if __name__ == "__main__":
    task = MonthlyPassTask()
    result = task.task_run()
    print(result.to_dict())