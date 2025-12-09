
from whimbox.common.cvars import IMG_RATE
from whimbox.common.utils.posi_utils import area_center
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.config.config import global_config
from whimbox.common.path_lib import find_game_launcher_folder
from whimbox.common.handle_lib import ProcessHandler
from whimbox.interaction.interaction_core import InteractionBGD
from whimbox.api.ocr_rapid import ocr
from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.ui.ui_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.task.background_task.background_task import background_manager

import subprocess, os, time

class StartGameTask(TaskTemplate):
    def __init__(self):
        super().__init__("start_game_task")

    @register_step("启动叠纸启动器")
    def step1(self):
        # 判断游戏是否已经在运行
        if HANDLE_OBJ.get_handle():
            return "step2"
        
        # 判断启动器是否已经在运行
        launcher_handle = ProcessHandler(process_name="xstarter.exe")
        if not launcher_handle.get_handle():
            launcher_path = global_config.get("Path", "launcher_path")
            if launcher_path == "":
                launcher_path = find_game_launcher_folder()
                launcher_path = os.path.join(launcher_path, "launcher.exe")
                if launcher_path == "":
                    self.task_stop("未能自动找到叠纸启动器路径，请手动打开游戏或在奇想盒设置中设置")
                    return
                else:
                    global_config.set("Path", "launcher_path", launcher_path)
                    global_config.save()
            
            if not os.path.exists(launcher_path):
                self.task_stop("未能自动找到叠纸启动器路径，请手动打开游戏或在奇想盒设置中设置")
                return

            subprocess.Popen(
                launcher_path, 
                creationflags=(
                    subprocess.DETACHED_PROCESS |
                    subprocess.CREATE_NO_WINDOW |
                    subprocess.CREATE_NEW_PROCESS_GROUP
                ),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True
            )
        
            launcher_handle = ProcessHandler(process_name="xstarter.exe")
            while not self.need_stop():
                time.sleep(1)
                if not launcher_handle.get_handle():
                    launcher_handle.refresh_handle()
                else:
                    break

        # 点击启动游戏按钮
        self.log_to_gui("叠纸启动器打开了")
        launcher_handle.set_foreground()
        launcher_itt = InteractionBGD(launcher_handle)
        cap = launcher_itt.capture()
        text_box_dict = ocr.detect_and_ocr(cap)
        if '启动游戏' in text_box_dict:
            target_box = text_box_dict['启动游戏']
            click_posi = area_center(target_box)
            launcher_itt.move_and_click(click_posi)
            self.log_to_gui("启动游戏成功")
        else:
            self.task_stop("未找到启动游戏按钮")
            return

    @register_step("进入游戏")
    def step2(self):
        # 等待游戏窗口出现
        self.log_to_gui("等待游戏窗口出现，等待分辨率恢复正常")
        while not self.need_stop() and not background_manager.is_game_started:
            time.sleep(1)
        if itt.get_img_existence(IconPageMainFeature):
            self.log_to_gui("成功进入游戏")
            return
        # 检测是否在登录界面了
        while not self.need_stop():
            time.sleep(1)
            if itt.get_img_existence(IconPageLoginFeature):
                break
        # 不停点击，直到进入loading界面
        while not self.need_stop():
            time.sleep(1)
            itt.move_and_click((100, 100))
            if itt.get_img_existence(IconUILoading):
                break
        self.log_to_gui("加载游戏中……")
        while not self.need_stop():
            time.sleep(1)
            if not itt.get_img_existence(IconUILoading):
                break
        self.log_to_gui("加载完成")
        # 不停点击，尝试点掉月卡界面，直到出现主界面
        while not self.need_stop():
            time.sleep(1)
            itt.move_and_click((1920/2, 1080/2))
            if itt.get_img_existence(IconPageMainFeature):
                break
        self.log_to_gui("成功进入游戏")

    def handle_finally(self):
        pass

if __name__ == "__main__":
    start_game_task = StartGameTask()
    start_game_task.task_run()