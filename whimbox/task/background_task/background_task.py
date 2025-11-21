"""
后台任务系统

功能：
1. 常驻后台自动检测画面，根据画面调用对应的task
2. 支持 / 键停止
3. 如果有其他前台task，自动暂停该后台task，前台task结束后自动继续
4. 可以通过ui来动态启用功能，比如：自动钓鱼，自动对话

设计思路：
- 后台任务通过检测 current_stop_flag 来判断是否有前台任务在运行
- 如果 current_stop_flag 不是后台任务自己的，说明有前台任务在运行，则暂停
- 前台任务结束后，current_stop_flag 会被清空，后台任务自动恢复
"""

import time
import threading
from enum import Enum
from whimbox.task.task_template import TaskTemplate, register_step, STATE_TYPE_STOP
from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import *
from whimbox.action.fishing import FishingTask
from whimbox.common.logger import logger
from whimbox.common.cvars import has_foreground_task
import contextvars


class BackgroundFeature(Enum):
    """后台功能枚举"""
    AUTO_FISHING = "auto_fishing"
    AUTO_DIALOGUE = "auto_dialogue"


class BackgroundTaskManager:
    """后台任务管理器 - 单例模式"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # 后台任务实例
        self.background_task = None
        self.background_thread = None
        
        # 功能开关（默认全部关闭）
        self.enabled_features = {
            BackgroundFeature.AUTO_FISHING: False,
            BackgroundFeature.AUTO_DIALOGUE: False,
        }
    
    def set_feature_enabled(self, feature: BackgroundFeature, enabled: bool):
        """设置功能开关"""
        with self._lock:
            self.enabled_features[feature] = enabled
            logger.info(f"后台功能 {feature.value} {'启用' if enabled else '禁用'}")
    
    def is_feature_enabled(self, feature: BackgroundFeature) -> bool:
        """检查功能是否启用"""
        return self.enabled_features.get(feature, False)
    
    def start_background_task(self):
        """启动后台任务"""
        with self._lock:
            if self.background_task is not None and not self.background_task.need_stop():
                logger.warning("后台任务已在运行")
                return False
            
            # 创建新的后台任务
            self.background_task = BackgroundTask(self)
            
            # 在新线程中运行
            self.background_thread = threading.Thread(
                target=self._run_background_task,
                daemon=True
            )
            self.background_thread.start()
            logger.info("后台任务已启动")
            return True
    
    def _run_background_task(self):
        """在独立线程中运行后台任务"""
        try:
            # 为后台任务线程创建新的 context
            ctx = contextvars.copy_context()
            ctx.run(self.background_task.task_run)
        except Exception as e:
            logger.error(f"后台任务运行出错: {e}")
    
    def stop_background_task(self):
        """停止后台任务"""
        with self._lock:
            if self.background_task is None:
                logger.warning("后台任务未运行")
                return False
            
            self.background_task.task_stop()
            logger.info("后台任务已停止")
            return True
    
    def is_running(self) -> bool:
        """检查后台任务是否在运行"""
        return (self.background_task is not None 
                and not self.background_task.need_stop())


# 全局后台任务管理器实例
background_manager = BackgroundTaskManager()


class BackgroundTask(TaskTemplate):
    """后台任务 - 自动检测画面并执行对应功能"""
    
    def __init__(self, manager: BackgroundTaskManager):
        super().__init__("background_task")
        self.manager = manager
        self.check_interval = 1.0  # 画面检测间隔（秒）
        self.last_pause_log_time = 0  # 上次打印暂停日志的时间
        self.was_paused = False  # 上一次循环是否处于暂停状态
    
    @register_step()
    def step_main_loop(self):
        """主循环 - 持续检测画面并触发对应功能"""
        while not self.need_stop():
            # 检测是否有前台任务在运行
            if has_foreground_task():
                # 有前台任务在运行，暂停后台任务
                if not self.was_paused:
                    # 刚进入暂停状态
                    logger.info("检测到前台任务运行，后台任务暂停")
                    self.was_paused = True
                time.sleep(1)
                continue
            else:
                # 没有前台任务
                if self.was_paused:
                    # 刚从暂停状态恢复
                    logger.info("前台任务结束，后台任务恢复运行")
                    self.was_paused = False
            
            if self.need_stop():
                break
            
            logger.info("后台任务运行中...")

            # 检测各种画面状态
            try:
                if self.manager.is_feature_enabled(BackgroundFeature.AUTO_FISHING):
                    # if self._detect_fishing_opportunity():
                    #     self._execute_fishing()
                    pass
                
                if self.manager.is_feature_enabled(BackgroundFeature.AUTO_DIALOGUE):
                    # if self._detect_dialogue_opportunity():
                    #     self._execute_dialogue()
                    pass
                        
            except Exception as e:
                logger.error(f"后台任务检测出错: {e}")
            
            # 等待一段时间再检测
            time.sleep(self.check_interval)
    
    def _detect_fishing_opportunity(self) -> bool:
        """检测是否可以钓鱼"""
        try:
            # 检测钓鱼图标
            if itt.get_img_existence(IconFishingFinish):
                return True
        except Exception as e:
            logger.debug(f"钓鱼检测失败: {e}")
        return False
    
    def _detect_dialogue_opportunity(self) -> bool:
        """检测是否出现对话框"""
        # TODO: 实现对话框检测逻辑
        # 需要检测对话框相关的UI元素
        return False
    
    def _execute_fishing(self):
        """执行钓鱼任务"""
        self.log_to_gui("检测到钓鱼机会，开始自动钓鱼")
        try:
            fishing_task = FishingTask()
            result = fishing_task.task_run()
            if result.message:
                self.log_to_gui(f"钓鱼完成: {result.message}")
        except Exception as e:
            logger.error(f"自动钓鱼出错: {e}")
    
    def _execute_dialogue(self):
        """执行对话任务"""
        self.log_to_gui("检测到对话，自动点击")
        try:
            # TODO: 实现自动对话逻辑
            from whimbox.common.keybind import keybind
            itt.key_press(keybind.KEYBIND_INTERACTION)
        except Exception as e:
            logger.error(f"自动对话出错: {e}")
    
    def task_stop(self, message=None, data=None):
        """停止后台任务"""
        super().task_stop()
    
    def handle_finally(self):
        # 后台任务结束时，什么都不需要做
        pass


if __name__ == "__main__":
    # 测试代码
    manager = background_manager
    
    # 启用自动钓鱼和自动采集
    manager.set_feature_enabled(BackgroundFeature.AUTO_FISHING, True)
    manager.set_feature_enabled(BackgroundFeature.AUTO_PICKUP, True)
    
    # 启动后台任务
    manager.start_background_task()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_background_task()

