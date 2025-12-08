from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.interaction.interaction_core import itt
from whimbox.common.scripts_manager import *
from whimbox.common.logger import logger
from whimbox.common.utils.utils import load_json
from whimbox.common.path_lib import SCRIPT_PATH
import time
from whimbox.common.scripts_manager import *


class RunMacroTask(TaskTemplate):
    """运行宏记录的任务"""
    
    def __init__(self, macro_filename: str, check_stop_func=None):
        super().__init__("run_macro_task")
        self.check_stop_func = check_stop_func
        
        self.macro_record = scripts_manager.query_macro(macro_filename)
        if self.macro_record is None:
            raise ValueError(f"宏\"{macro_filename}\"不存在")
        self.current_step_index = 0
        self.pressing_keys = set()
    
    def _execute_step(self, step: MacroStep):
        """执行单个宏步骤"""
        try:
            if step.type == "keyboard":
                # 键盘操作
                if step.action == "press":
                    itt.key_down(step.key)
                    logger.debug(f"执行键盘按下: {step.key}")
                    self.pressing_keys.add(step.key)
                    time.sleep(0.1)
                elif step.action == "release":
                    itt.key_up(step.key)
                    logger.debug(f"执行键盘松开: {step.key}")
                    self.pressing_keys.discard(step.key)
                    
            elif step.type == "mouse_button":
                # 鼠标按键操作
                # 窗口内坐标直接使用，itt会自动处理坐标转换
                if step.position:
                    # 移动到目标位置并点击
                    if step.action == "press":
                        if step.key == "left":
                            itt.move_to(step.position)
                            time.sleep(0.1)
                            itt.left_down()
                            logger.debug(f"执行鼠标左键按下 at {step.position}")
                            self.pressing_keys.add("left")
                            time.sleep(0.1)
                        elif step.key == "right":
                            itt.move_to(step.position)
                            time.sleep(0.1)
                            itt.right_down()
                            logger.debug(f"执行鼠标右键按下 at {step.position}")
                            self.pressing_keys.add("right")
                            time.sleep(0.1)
                        elif step.key == "middle":
                            itt.move_to(step.position)
                            time.sleep(0.1)
                            # 中键操作
                            pass
                            
                    elif step.action == "release":
                        if step.key == "left":
                            itt.left_up()
                            logger.debug(f"执行鼠标左键松开 at {step.position}")
                            self.pressing_keys.discard("left")
                        elif step.key == "right":
                            itt.right_up()
                            logger.debug(f"执行鼠标右键松开 at {step.position}")
                            self.pressing_keys.discard("right")
                        elif step.key == "middle":
                            pass
                    
        except Exception as e:
            logger.error(f"执行步骤失败: {e}, step: {step}")
        
    @register_step(state_msg="执行宏操作")
    def execute_macro(self):
        """执行宏操作"""
        offset = self.macro_record.info.offset
        start_time = time.time()
        last_timestamp = 0.0
        
        for i, step in enumerate(self.macro_record.steps):
            if self.need_stop():
                break
            if self.check_stop_func and self.check_stop_func():
                break
            
            self.current_step_index = i
            step_timestamp = step.timestamp + offset
            
            # 等待到达该步骤的时间点
            time_to_wait = step_timestamp - last_timestamp
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            
            # 执行步骤
            self._execute_step(step)
            
            last_timestamp = step_timestamp
        
        execution_time = time.time() - start_time
        self.log_to_gui(f"宏执行结束！耗时: {execution_time:.2f}秒")
    
    def handle_finally(self):
        """清理资源"""
        for key in self.pressing_keys:
            itt.key_up(key)
        # 不调用父类的 handle_finally，因为不需要返回主界面

if __name__ == "__main__":
    task = RunMacroTask("朝夕心愿_小游戏_穿梭大冒险_宏.json")
    task.task_run()