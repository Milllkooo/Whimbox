from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import TextFPickUp
from whimbox.common.cvars import DEBUG_MODE
from whimbox.common.utils.ui_utils import skip_to_page_main
from whimbox.common.keybind import keybind

class PickupTask(TaskTemplate):
    def __init__(self):
        super().__init__("pickup_task")
        self.material_count_dict = {}

    @register_step("开始采集")
    def step1(self):
        while not self.need_stop():
            texts = itt.ocr_multiple_lines(TextFPickUp.cap_area)
            # 预处理texts，去除非中文的元素
            texts = [text for text in texts if any('\u4e00' <= char <= '\u9fff' for char in text)]
            
            if len(texts) == 2 and texts[1] == TextFPickUp.text:
                pickup_item = texts[0]
                if pickup_item in self.material_count_dict:
                    self.material_count_dict[pickup_item] += 1
                else:
                    self.material_count_dict[pickup_item] = 1
                if DEBUG_MODE:
                    # debug模式下，不采集，这样可以多测几遍
                    itt.delay(0.5, comment="等待采集完成")
                    break
                else:
                    itt.key_press(keybind.KEYBIND_INTERACTION)
                    itt.delay(0.5, comment="等待采集完成")
                    skip_to_page_main() # 获取到新物品时会弹出窗口，快速跳过
            else:
                break
        
        if len(self.material_count_dict) == 0:
            self.update_task_result(message="未采集到物品")
            self.log_to_gui("未采集到物品")
            return
        count_str_list = []
        for key, value in self.material_count_dict.items():
            count_str_list.append(f"{key}x{value}")
        res = ",".join(count_str_list)
        res = f"获得{res}"
        self.update_task_result(
            message=res,
            data=self.material_count_dict
        )
        self.log_to_gui(res)

if __name__ == "__main__":
    while True:
        pickup_task = PickupTask()
        pickup_task.task_run()