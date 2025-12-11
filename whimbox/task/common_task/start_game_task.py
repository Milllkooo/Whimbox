
from whimbox.task.task_template import *
from whimbox.config.config import global_config
from whimbox.common.path_lib import find_game_launcher_folder
from whimbox.common.handle_lib import ProcessHandler
from whimbox.interaction.interaction_core import InteractionBGD
from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.ui.ui import ui_control
from whimbox.ui.ui_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.task.background_task.background_task import background_manager
from whimbox.common.logger import logger
from whimbox.common.utils.posi_utils import area_center

import os, time

class StartGameTask(TaskTemplate):
    def __init__(self):
        super().__init__("start_game_task")

    @register_step("启动叠纸启动器")
    def step1(self):
        # 判断游戏是否已经在运行
        if HANDLE_OBJ.get_handle():
            # self.update_task_result(status=STATE_TYPE_SUCCESS, message="游戏已经在运行，无需自动启动")
            return
        
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

            # subprocess.Popen(
            #     launcher_path, 
            #     creationflags=(
            #         subprocess.DETACHED_PROCESS |
            #         subprocess.CREATE_NO_WINDOW |
            #         subprocess.CREATE_NEW_PROCESS_GROUP
            #     ),
            #     stdin=subprocess.DEVNULL,
            #     stdout=subprocess.DEVNULL,
            #     stderr=subprocess.DEVNULL,
            #     close_fds=True
            # )
            try:
                os.startfile(launcher_path)
            except Exception as e:
                logger.error(f"打开叠纸启动器失败: {e}")
                self.task_stop(f"打开叠纸启动器失败, 请手动打开游戏")
                return
            
            self.log_to_gui("等待叠纸启动器启动")
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
        retry_time = 10
        while not self.need_stop() and retry_time > 0:
            time.sleep(1)
            text = launcher_itt.ocr_single_line(AreaLaunchButton)
            if text == "":
                retry_time -= 1
                continue
            else:
                if text != "启动游戏":
                    # 点击更新，直到按钮变成“启动游戏”
                    self.log_to_gui("更新游戏中……")
                    launcher_itt.move_and_click(AreaLaunchButton.center_position())
                    while not self.need_stop():
                        time.sleep(1)
                        text = launcher_itt.ocr_single_line(AreaLaunchButton)
                        if text == "启动游戏":
                            break
                launcher_itt.move_and_click(AreaLaunchButton.center_position())
                self.log_to_gui("点击启动游戏按钮成功")
                break
        if retry_time <= 0:
            self.task_stop("未找到启动游戏按钮")
            return

    @register_step("等待游戏窗口出现，等待分辨率恢复正常")
    def step2(self):
        retry_time = 10
        while not self.need_stop():
            time.sleep(5)
            if background_manager.is_game_started:
                retry_time -= 1
                shape_ok, width, height = HANDLE_OBJ.check_shape()
                if shape_ok or width/height == 1920/1080: # 条件放宽，有些电脑不进入游戏不会恢复分辨率
                    HANDLE_OBJ.set_foreground()
                    break
                else:
                    if retry_time == 8:
                        self.log_to_gui(f"当前游戏分辨率为{width}x{height}，请等待分辨率恢复正常，或手动设置游戏的显示模式设置为窗口模式，分辨率设置为1920x1080或2560x1440")
                    if retry_time <= 0:
                        self.task_stop(f"当前游戏分辨率为{width}x{height}，请先将游戏的显示模式设置为窗口模式，分辨率设置为1920x1080或2560x1440")
                        return

    @register_step("进入游戏")
    def step3(self):
        # 检测是否已经进入游戏
        if ui_control.is_valid_page():
            self.update_task_result(status=STATE_TYPE_SUCCESS, message="成功进入游戏")
            return STEP_NAME_FINISH

        def click_box(box, parent_area):
            offset = (parent_area.position[0], parent_area.position[1])
            center = area_center(box)
            center = (center[0] + offset[0], center[1] + offset[1])
            itt.move_and_click(center)

        # 检测是否在登录界面
        while not self.need_stop():
            time.sleep(1)
            text_box_dict = itt.ocr_and_detect_posi(AreaLoginOCR)
            if "点击进入游戏" in text_box_dict:
                click_box(text_box_dict["点击进入游戏"], AreaLoginOCR)
                break
            if "确认" in text_box_dict:
                self.log_to_gui("发现新版本，开始更新")
                click_box(text_box_dict["确认"], AreaLoginOCR)
                return "step2"
            else:
                itt.key_press('esc')
        # 不停点击，直到进入loading界面
        while not self.need_stop():
            time.sleep(1)
            itt.move_and_click((100, 100))
            if itt.get_img_existence(IconUILoading):
                break
    
    @register_step("加载游戏中……")
    def step4(self):
        while not self.need_stop():
            time.sleep(1)
            if not itt.get_img_existence(IconUILoading):
                self.log_to_gui("加载完成")
                break
        # 不停点击，尝试点掉月卡界面，直到出现主界面
        while not self.need_stop():
            time.sleep(1)
            itt.move_and_click((1920/2, 1080/2))
            if itt.get_img_existence(IconPageMainFeature):
                self.update_task_result(status=STATE_TYPE_SUCCESS, message="成功进入游戏")
                break

    def handle_finally(self):
        pass

if __name__ == "__main__":
    start_game_task = StartGameTask()
    start_game_task.task_run()