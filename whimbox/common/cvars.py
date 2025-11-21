"""Constants."""

import threading
import contextvars
from whimbox.common.path_lib import IS_DEV_MODE
from whimbox.config.config import global_config

DEBUG_MODE = global_config.get_bool('General', 'debug') and IS_DEV_MODE
CV_DEBUG_MODE = global_config.get_bool('General', 'cv_debug') and IS_DEV_MODE

# 使用 contextvars 来存储当前任务的 stop_flag
# 这样每个任务都有独立的 stop_flag，无需在每个函数中显式传递
current_stop_flag: contextvars.ContextVar[threading.Event] = contextvars.ContextVar(
    'current_stop_flag', 
    default=None
)

def get_current_stop_flag() -> threading.Event:
    """获取当前上下文的 stop_flag
    
    如果当前上下文没有设置 stop_flag，返回一个永远不会被设置的 flag
    这样可以保证代码在没有 task 上下文时也能正常运行
    """
    flag = current_stop_flag.get()
    if flag is None:
        # 如果没有设置，创建一个永远不会被设置的 flag
        flag = threading.Event()
    return flag

MCP_TOOL_TIMEOUT = 24*60*60  # mcp工具调用超时时间设为24小时

# Angle modes
ANGLE_NORMAL = 0
ANGLE_NEGATIVE_Y = 1
ANGLE_NEGATIVE_X = 2
ANGLE_NEGATIVE_XY = 3

# Process name
PROCESS_NAME = 'X6Game-Win64-Shipping.exe'

# log
LOG_NONE = 0
LOG_WHEN_TRUE = 1
LOG_WHEN_FALSE = 2
LOG_ALL = 3

IMG_RATE = 0
IMG_POSI = 1
IMG_POINT = 2
IMG_RECT = 3
IMG_BOOL = 4
IMG_BOOLRATE = 5

NORMAL_CHANNELS = 0
FOUR_CHANNELS = 40000

THREAD_PAUSE_SET_FLAG_ONLY = 0
THREAD_PAUSE_FORCE_TERMINATE = 1

# 字符串匹配模式
CONTAIN_MATCHING = 0
ACCURATE_MATCHING = 1