# 每周幻境

from whimbox.task.task_template import *
from whimbox.ui.page_assets import page_daily_task, page_huanjing_weekly
from whimbox.ui.ui import ui_control
from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import *
from whimbox.common.utils.ui_utils import *

class WeeklyRealmTask(TaskTemplate):
    def __init__(self):
        super().__init__("weekly_realm_task")

    @register_step("检查每周幻境完成情况")
    def step1(self):
        ui_control.goto_page(page_daily_task)
        weekly_count_str = itt.ocr_single_line(AreaWeeklyCountText)
        try:
            weekly_count_str = weekly_count_str.replace('v', '').replace('V', '').replace(' ', '')
            finished_count = int(weekly_count_str.split("/")[0])
            total_count = int(weekly_count_str.split("/")[1])
            self.log_to_gui(f"每周幻境完成情况: {finished_count}/{total_count}")
        except:
            raise Exception(f"每周幻境完成数量识别异常:{weekly_count_str}")
        # if finished_count < total_count:
        #     return
        # else:
        #     return "step5"
    
    @register_step("前往心之突破幻境")
    def step2(self):
        ui_control.goto_page(page_huanjing_weekly)
    
    def quick_challenge(self, level_name):
        if not scroll_find_click(AreaBlessHuanjingLevelsSelect, level_name, str_match_mode=1):
            self.log_to_gui(f"未找到{level_name}", is_error=True)
            return False
        if not wait_until_appear_then_click(ButtonBlessHuanjingQuickPlay):
            self.log_to_gui("未找到快速挑战按钮", is_error=True)
            return False
        else:
            itt.delay(0.5, comment="等待窗口弹出")
            if not wait_until_appear_then_click(ButtonHuanjingConfirm):
                self.log_to_gui("未找到注入能量按钮", is_error=True)
                wait_until_appear_then_click(ButtonHuanjingCancel)
                return False
        if skip_get_award():
            self.log_to_gui(f"{level_name}完成")
            return True
        else:
            raise Exception("领取奖励失败")

    @register_step("快速挑战奇格格达")
    def step3(self):
        return self.quick_challenge("奇格格达")
    
    @register_step("快速挑战卷卷")
    def step4(self):
        return self.quick_challenge("卷卷")

    @register_step("完成每周幻境")
    def step5(self):
        self.log_to_gui("每周幻境已完成")
        self.update_task_result(message="每周幻境已完成", data=True)

if __name__ == "__main__":
    task = WeeklyRealmTask()
    task_result = task.task_run()
    print(task.task_result)
