from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.common.keybind import keybind
from whimbox.ui.ui_assets import IconSkipDialog
from whimbox.interaction.interaction_core import itt
import time

class SkipDialogTask(TaskTemplate):
    def __init__(self):
        super().__init__("skip_dialog_task")

    @register_step()
    def step1(self):
        while not self.need_stop():
            if itt.get_img_existence(IconSkipDialog):
                itt.key_press(keybind.KEYBIND_INTERACTION)
            else:
                break
            time.sleep(0.25)
    
    def handle_finally(self):
        pass

if __name__ == "__main__":
    task = SkipDialogTask()
    task.task_run()