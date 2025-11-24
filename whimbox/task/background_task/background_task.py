import time
import threading
from enum import Enum
from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import *
from whimbox.action.fishing import FishingTask
from whimbox.action.skip_dialog import SkipDialogTask
from whimbox.common.logger import logger
from whimbox.common.cvars import has_foreground_task
from whimbox.common.utils.img_utils import crop
from whimbox.task.task_template import STATE_TYPE_SUCCESS
from whimbox.common.cvars import current_stop_flag


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
            if self.background_task is not None and self.background_task.is_running():
                logger.warning("后台任务已在运行")
                return False
            
            # 创建新的后台任务
            self.background_task = BackgroundTask(self)
            
            # 在新线程中运行
            self.background_thread = threading.Thread(
                target=self.background_task.run,
                daemon=True
            )
            self.background_thread.start()
            logger.info("后台任务已启动")
            return True
    
    def stop_background_task(self):
        """停止后台任务"""
        with self._lock:
            if self.background_task is None:
                logger.warning("后台任务未运行")
                return False
            
            self.background_task.stop()
            logger.info("后台任务已停止")
            return True
    
    def is_running(self) -> bool:
        """检查后台任务是否在运行"""
        return (self.background_task is not None 
                and self.background_task.is_running())


# 全局后台任务管理器实例
background_manager = BackgroundTaskManager()


class BackgroundTask:
    """后台任务 - 自动检测画面并执行对应功能"""
    
    def __init__(self, manager: BackgroundTaskManager):
        self.manager = manager
        self.check_interval = 1.0  # 画面检测间隔（秒）
        self.was_paused = False  # 上一次循环是否处于暂停状态
        self.stop_event = threading.Event()  # 停止事件

    def log_to_gui(self, msg, is_error=False, type="update_ai_message"):
        from whimbox.ingame_ui.ingame_ui import win_ingame_ui
        if is_error:
            msg = f"❌ {msg}\n"
        else:
            msg = f"✅ {msg}\n"
        if win_ingame_ui:
            win_ingame_ui.update_message(msg, type)
        logger.info(msg)

    def stop(self):
        """停止后台任务"""
        self.stop_event.set()
    
    def is_running(self) -> bool:
        """检查是否在运行"""
        return not self.stop_event.is_set()
    
    def run(self):
        """主循环 - 持续检测画面并触发对应功能"""
        try:            
            while not self.stop_event.is_set():
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
                
                # 检测各种画面状态
                try:
                    cap = itt.capture()
                    
                    # 检测钓鱼状态
                    if self.manager.is_feature_enabled(BackgroundFeature.AUTO_FISHING):
                        if self._detect_fishing_opportunity(cap):
                            self._execute_fishing()            
                    
                    # 检测对话状态
                    if self.manager.is_feature_enabled(BackgroundFeature.AUTO_DIALOGUE):
                        if self._detect_dialogue_opportunity(cap):
                            self._execute_dialogue()
                            
                except Exception as e:
                    logger.error(f"后台任务检测出错: {e}")
                
                # 等待一段时间再检测
                time.sleep(self.check_interval)
        
        except Exception as e:
            logger.error(f"后台任务运行出错: {e}")
        finally:
            logger.info("后台任务已停止")
    
    def _detect_fishing_opportunity(self, cap) -> bool:
        """检测是否可以钓鱼"""
        cap = crop(cap, AreaFishingIcons.position)
        if itt.get_img_existence(IconFishingFinish, cap=cap):
            return True
        return False
    
    def _execute_fishing(self):
        """执行钓鱼任务"""
        try:
            self.log_to_gui("检测到钓鱼界面，开始自动钓鱼", type="add_ai_message")
            fishing_task = FishingTask()
            fishing_task.step2()
             # 因为不是完整的task运行流程，所以手动清除current_stop_flag
            current_stop_flag.set(None)
            if fishing_task.task_result.status == STATE_TYPE_SUCCESS:
                self.log_to_gui(f"自动钓鱼完成: {fishing_task.task_result.message}", type="finalize_ai_message")
            else:
                self.log_to_gui(f"自动钓鱼失败: {fishing_task.task_result.message}", type="finalize_ai_message")
        except Exception as e:
            logger.error(f"自动钓鱼出错: {e}")

    def _detect_dialogue_opportunity(self, cap) -> bool:
        """检测是否进入对话"""
        cap = crop(cap, IconSkipDialog.cap_posi)
        if itt.get_img_existence(IconSkipDialog, cap=cap):
            return True
        return False
    
    def _execute_dialogue(self):
        """执行对话任务"""
        # self.log_to_gui("检测到对话界面，开始自动对话", type="add_ai_message")
        skip_dialog_task = SkipDialogTask()
        skip_dialog_task.task_run()
        # self.log_to_gui(f"自动对话结束", type="finalize_ai_message")


if __name__ == "__main__":
    # 测试代码
    manager = background_manager
    
    # 启用自动钓鱼
    manager.set_feature_enabled(BackgroundFeature.AUTO_FISHING, True)
    
    # 启动后台任务
    manager.start_background_task()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_background_task()
