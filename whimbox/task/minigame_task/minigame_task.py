# 穿梭大冒险

from unittest import skip
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.common.keybind import keybind
from whimbox.common.utils.ui_utils import *
from whimbox.task.macro_task.run_macro_task import RunMacroTask
from whimbox.common.utils.utils import *
from whimbox.common.scripts_manager import *


class MinigameTask(TaskTemplate):
    def __init__(self, macro_name: str):
        super().__init__("minigame_task")
        self.max_retry_times = 2
        self.retry_times = 0
        self.macro_name = macro_name

    @register_step("与NPC对话开始小游戏")
    def step1(self):
        itt.delay(1, comment="等待对话交互按钮出现")
        itt.key_press(keybind.KEYBIND_INTERACTION)
        wait_until_appear(IconSkipDialog, 5)
        if itt.get_img_existence(IconPageMainFeature):
            raise Exception("未进入NPC对话")
        skip_dialog()
        if not scroll_find_click(AreaDialogSelection, "开始游戏", str_match_mode=1):
            raise Exception("未找到对话选项：开始游戏")
        skip_dialog()
        if not scroll_find_click(AreaDialogSelection, "没问题", str_match_mode=1):
            raise Exception("未找到对话选项：支付噗灵")
        skip_dialog()

    @register_step("开始小游戏")
    def step2(self):
        while not self.need_stop():
            time.sleep(0.2)
            if itt.get_img_existence(IconPageMainFeature):
                break
        logger.info("可以开始动了")
        
        def check_stop_func():
            return not itt.get_img_existence(IconPageMainFeature)

        task = RunMacroTask(self.macro_name, check_stop_func=check_stop_func)
        task.task_run()
    
    @ register_step("检查是否失败")
    def step3(self):
        if itt.get_img_existence(ButtonMinigameRetry):
            if self.retry_times > self.max_retry_times:
                self.log_to_gui(f"小游戏已重试{self.max_retry_times}次，依旧失败，只能退出了")
                wait_until_appear_then_click(ButtonMinigameQuit)
                return 'step4'
            else:
                self.retry_times += 1
                self.log_to_gui(f"小游戏失败了，再试一遍")
                itt.appear_then_click(ButtonMinigameRetry)
                time.sleep(0.5)
                wait_until_appear_then_click(ButtonMinigameRetryOk)
                return 'step2'
        else:
            self.log_to_gui("小游戏成功了")
            return 'step4'

    @ register_step("结束小游戏")
    def step4(self):
        wait_until_appear(IconSkipDialog, 10)
        skip_dialog()
        if skip_get_award():
            self.update_task_result(message="成功领取小游戏奖励")
        else:
            raise Exception("领取小游戏奖励失败")
        skip_dialog()
        if not scroll_find_click(AreaDialogSelection, "谢谢你", str_match_mode=1):
            raise Exception("未找到对话选项：不了")
        skip_dialog()
        wait_until_appear(IconPageMainFeature, 3)

if __name__ == "__main__":
    task = MinigameTask("朝夕心愿_小游戏_穿梭大冒险_宏")
    task.task_run()