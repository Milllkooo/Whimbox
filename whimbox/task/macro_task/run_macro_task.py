from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.interaction.interaction_core import itt
from whimbox.common.scripts_manager import *
from whimbox.common.logger import logger
import time
from whimbox.common.scripts_manager import *
from whimbox.common.handle_lib import HANDLE_OBJ


class RunMacroTask(TaskTemplate):
    """运行宏记录的任务"""
    
    def __init__(self, macro_filename: str, delay=0, check_stop_func=None):
        super().__init__("run_macro_task")
        self.check_stop_func = check_stop_func
        self.delay = delay
        self.macro_record = scripts_manager.query_macro(macro_filename)
        if self.macro_record is None:
            raise ValueError(f"宏\"{macro_filename}\"不存在，请先下载该宏")
        self.current_step_index = 0
        self.pressing_keys = set()
    
    def _execute_step(self, step: MacroStep):
        """执行单个宏步骤"""
        try:
            if step.type == "keyboard":
                # 键盘操作
                if step.action == "press":
                    itt.key_down(step.key)
                    self.pressing_keys.add(step.key)
                elif step.action == "release":
                    itt.key_up(step.key)
                    self.pressing_keys.discard(step.key)
                    
            elif step.type == "mouse_button":
                # 鼠标按键操作
                if step.position:
                    # 移动到目标位置并点击
                    if step.action == "press":
                        itt.move_to(step.position)
                        itt.key_down(step.key)
                        self.pressing_keys.add(step.key)
                    elif step.action == "release":
                        itt.key_up(step.key)
                        self.pressing_keys.discard(step.key)
                    
        except Exception as e:
            logger.error(f"执行步骤失败: {e}, step: {step}")
    
    @register_step(state_msg="执行宏操作")
    def execute_macro(self):
        aspect_ratio = self.macro_record.info.aspect_ratio
        _, width, height = HANDLE_OBJ.check_shape()
        if aspect_ratio == "16:9" and not (1.70<width/height<1.80):
            self.log_to_gui(f"宏\"{self.macro_record.info.name}\"只支持16:9分辨率，请修改游戏设置", is_error=True)
            return
        elif aspect_ratio == "16:10" and not (1.55<width/height<1.65):
            self.log_to_gui(f"宏\"{self.macro_record.info.name}\"只支持16:10分辨率，请修改游戏设置", is_error=True)
            return

        # 执行宏操作
        offset = self.macro_record.info.offset + self.delay
        start_time = time.time()
        
        for i, step in enumerate(self.macro_record.steps):
            if self.need_stop():
                break
            if self.check_stop_func and self.check_stop_func():
                break
            
            self.current_step_index = i
            step_timestamp = step.timestamp + offset
            
            # 计算该步骤应该执行的绝对时间点
            target_time = start_time + step_timestamp
            current_time = time.time()
            time_to_wait = target_time - current_time
            
            # 等待到达该步骤的时间点
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            
            # 执行步骤
            self._execute_step(step)
        
        execution_time = time.time() - start_time
        self.log_to_gui(f"宏执行结束！耗时: {execution_time:.2f}秒")
    
    def handle_finally(self):
        """清理资源"""
        for key in self.pressing_keys:
            itt.key_up(key)
        # 不调用父类的 handle_finally，因为不需要返回主界面

if __name__ == "__main__":
    task = RunMacroTask("我的宏_20251222214158")
    task.task_run()