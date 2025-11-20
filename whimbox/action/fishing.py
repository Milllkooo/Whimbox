import time
from enum import Enum
import cv2
import re

from whimbox.common.cvars import CV_DEBUG_MODE
from whimbox.common.timer_module import AdvanceTimer
from whimbox.common.utils.ui_utils import skip_to_page_main
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.interaction.interaction_core import itt
from whimbox.ui.page_assets import page_main
from whimbox.ui.ui import ui_control
from whimbox.ui.ui_assets import *
from whimbox.common.utils.img_utils import count_px_with_hsv_limit
from whimbox.common.utils.posi_utils import union_bbox
from whimbox.ability.ability import ability_manager
from whimbox.ability.cvar import ABILITY_NAME_FISH
from whimbox.common.logger import logger
from whimbox.common.keybind import keybind

hsv_limit = ([20, 50, 245], [30, 90, 255])

class FishingResult(Enum):
    SUCCESS = 0
    NO_FISH = 1
    WRONG_POSITION = 2

class FishingState(Enum):
    NOT_FISHING = 0
    FINISH = 1      # 收竿 (右键取消)
    STRIKE = 2      # 提竿 (S)
    PULL_LINE = 3   # 拉扯鱼线 (A/D)
    REEL_IN = 4     # 收线 (右键狂点)
    SKIP = 5        # 跳过 (F)
    UNKNOWN = 6

FISHING_STATE_MAPPING = [
    (IconFishingFinish, FishingState.FINISH),
    (IconFishingStrike, FishingState.STRIKE),
    (IconFishingPullLine, FishingState.PULL_LINE),
    (IconFishingPullLineAlt, FishingState.PULL_LINE),
    (IconFishingReelIn, FishingState.REEL_IN),
    (IconFishingSkip, FishingState.SKIP),
]

class FishingTask(TaskTemplate):
    def __init__(self, check_stop_func=None):
        super().__init__("fishing_task", check_stop_func)
        self.state_area = self.get_state_area()
        self.material_count_dict = {}

    def get_state_area(self):
        """获取状态判断区域"""
        bboxes = []
        for icon, _ in FISHING_STATE_MAPPING:
            bboxes.append(icon.bbg_posi)
        merged_bbox = union_bbox(*bboxes)
        return merged_bbox

    def check_target_state(self, target_icon):
        cap = itt.capture(posi=target_icon.bbg_posi)
        _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)
        if itt.get_img_existence(target_icon, cap=cap):
            return True


    def get_current_state(self):
        """在模板区域内检测当前状态"""
        cap = itt.capture(posi=self.state_area)
        _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)
        if CV_DEBUG_MODE:
            cv2.imshow("cap", cap)
            cv2.waitKey(1)

        for icon, state in FISHING_STATE_MAPPING:
            if itt.get_img_existence(icon, is_gray=True, cap=cap):
                return state

        return FishingState.UNKNOWN

    def _pull_in_direction(self, key, px_count):
        """
        按下一个按键并检查方向是否正确。
        如果正确，则持续按住
        """
        itt.key_down(key)
        while not self.need_stop():
            time.sleep(0.3)
            cap = itt.capture(posi=AreaFishingDetection.position)
            current_px_count = count_px_with_hsv_limit(cap, hsv_limit[0], hsv_limit[1])
            logger.debug(f"尝试方向: {key}, {px_count} -> {current_px_count}")
            if current_px_count <= px_count:
                px_count = current_px_count
                if px_count == 0:
                    break
                continue
            else:
                break
        itt.key_up(key)
        return px_count

    def handle_pull_line(self):
        """处理拉扯鱼线状态的核心逻辑"""
        self.log_to_gui("进入拉扯鱼线状态")
        cap = itt.capture(posi=AreaFishingDetection.position)
        px_count = count_px_with_hsv_limit(cap, hsv_limit[0], hsv_limit[1])
        while not self.need_stop():
            px_count = self._pull_in_direction('a', px_count)
            if not self.check_target_state(IconFishingPullLine):
                break
            px_count = self._pull_in_direction('d', px_count)
            if not self.check_target_state(IconFishingPullLine):
                break

    def handle_strike(self):
        self.log_to_gui("状态: 提竿")
        itt.key_press('s')

    def handle_reel_in(self):
        self.log_to_gui("状态: 收线")
        while True:
            if keybind.KEYBIND_FISHING_REEL_IN == "鼠标右键":
                itt.right_click()
            else:
                itt.key_press(keybind.KEYBIND_FISHING_REEL_IN)
            if not self.check_target_state(IconFishingReelIn):
                break
            # time.sleep(0.1)

    def handle_skip(self):
        self.log_to_gui("状态: 跳过")
        # while not ui_control.verify_page(page_main):
        #     itt.key_press(keybind.KEYBIND_INTERACTION)
        #     time.sleep(0.2)
        skip_to_page_main()
        self.record_material()

    def record_material(self):
        # 从“笔刷鱼×1.6kg”文本中提取鱼名，并记录数量
        # 为了和其他采集任务统一，这里不记录重量，而是个数
        texts = itt.ocr_multiple_lines(AreaMaterialGetText)
        for line in texts:
            pattern = r"^(.+?)[×xX]([0-9]+(?:\.[0-9]+)?)kg$"
            match = re.match(pattern, line)
            if match:
                fish_name = match.group(1)
                # fish_weight = float(match.group(2))
                # self.log_to_gui(f"获得{fish_name}x{fish_weight}kg")
                # if fish_name in self.material_count_dict:
                #     self.material_count_dict[fish_name] += fish_weight
                # else:
                #     self.material_count_dict[fish_name] = fish_weight
                self.log_to_gui(f"获得{fish_name}")
                if fish_name in self.material_count_dict:
                    self.material_count_dict[fish_name] += 1
                else:
                    self.material_count_dict[fish_name] = 1
                break


    @register_step("切换钓鱼能力")
    def step1(self):
        ability_manager.change_ability(ABILITY_NAME_FISH)

    @register_step("开始钓鱼")
    def step2(self):
        fish_time = 0
        while fish_time < 3 and not self.need_stop():
            res = self.fishing_loop()
            if res == FishingResult.SUCCESS:
                fish_time += 1
            elif res == FishingResult.NO_FISH:
                break
            elif res == FishingResult.WRONG_POSITION:
                break
        
        if len(self.material_count_dict) == 0:
            self.update_task_result(message="未钓到鱼")
            self.log_to_gui("未钓到鱼")
            return
        else:
            res = []
            for fish_name, fish_weight in self.material_count_dict.items():
                res.append(f"{fish_name}x{fish_weight}kg")
            res_str = ", ".join(res)
            self.update_task_result(message=f"获得{res_str}", data=self.material_count_dict)


    def fishing_loop(self):
        itt.right_click()
        # 等待进入钓鱼状态
        while self.get_current_state() != FishingState.FINISH and not self.need_stop():
            time.sleep(0.5)
        # 开始钓鱼
        logger.info("进入钓鱼状态")
        idle_timer = AdvanceTimer(10) # 10秒如果没有鱼，就说明钓鱼位置错了
        idle_timer.start()
        itt.delay(2, comment="等待弹出鱼钓光的提示框")
        if itt.get_img_existence(IconFishingNoFish):
            itt.right_click()
            while not ui_control.verify_page(page_main):
                time.sleep(0.5)
            return FishingResult.NO_FISH
        
        while not self.need_stop():
            if idle_timer.started() and idle_timer.reached():
                itt.right_click()
                while not ui_control.verify_page(page_main):
                    time.sleep(0.2)
                return FishingResult.WRONG_POSITION

            state = self.get_current_state()
            logger.debug(f"当前状态: {state}")
            if state in [FishingState.NOT_FISHING, FishingState.FINISH]:
                time.sleep(0.5)
                continue
            elif state == FishingState.STRIKE:
                idle_timer.clear()
                self.handle_strike()
                continue
            elif state == FishingState.PULL_LINE:
                self.handle_pull_line()
                continue
            elif state == FishingState.REEL_IN:
                self.handle_reel_in()
                continue
            elif state == FishingState.SKIP:
                self.handle_skip()
                break
            elif state == FishingState.UNKNOWN:
                self.handle_skip()
                break

        return FishingResult.SUCCESS


if __name__ == "__main__":
    # CV_DEBUG_MODE = True
    task = FishingTask()
    # task.task_run()
    task.fishing_loop()