from pydantic import BaseModel
from typing import Optional, Literal
import os
import json

from whimbox.common.path_lib import SCRIPT_PATH
from whimbox.common.logger import logger

# 基础脚本信息
class ScriptInfo(BaseModel):
    name: str 
    type: Optional[str] = None
    update_time: Optional[str] = None
    version: Optional[str] = None

# 跑图脚本信息
class PathInfo(ScriptInfo):
    target: Optional[str] = None # 目标：素材名
    count: Optional[int] = None # 目标数量
    region: Optional[str] = None
    map: Optional[str] = None

# 跑图脚本点位
class PathPoint(BaseModel):
    id: int
    move_mode: str          # 移动模式：行走、跳跃、飞行
    point_type: str      # 点位类型：途径点、必经点
    action: Optional[str] = None
    action_params: Optional[str] = None
    position: list[float]

# 跑图脚本
class PathRecord(BaseModel):
    info: PathInfo
    points: list[PathPoint]

# 宏脚本信息
class MacroInfo(ScriptInfo):
    offset: Optional[float] = 0.0  # 整体偏移时间

# 宏脚本步骤
class MacroStep(BaseModel):
    type: Literal["keyboard", "mouse_button"]  # 操作类型
    key: Optional[str] = None  # 键盘按键名称或鼠标按键名称（left/right/middle）
    action: Optional[Literal["press", "release"]] = None  # 按键动作：按下/松开
    position: Optional[tuple[int, int]] = None  # 鼠标位置（窗口内坐标，1920x1080标准分辨率）
    timestamp: float  # 时间戳（相对于录制开始的秒数）

# 宏脚本
class MacroRecord(BaseModel):
    info: MacroInfo
    steps: list[MacroStep] = []  # 操作步骤列表


class ScriptsManager:

    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(ScriptsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.path_dict = {}
        self.macro_dict = {}
        self.init_scripts_dict()

        self._initialized = True

    def init_scripts_dict(self):
        self.path_dict = {}
        self.macro_dict = {}
        for file in os.listdir(SCRIPT_PATH):
            if file.endswith(".json"):
                with open(os.path.join(SCRIPT_PATH, file), "r", encoding="utf-8") as f:
                    try:
                        json_text = f.read()
                        json_dict = json.loads(json_text)
                        if json_dict['info']['type'] == 'macro':
                            macro_record = MacroRecord.model_validate_json(json_text)
                            macro_name = macro_record.info.name
                            if macro_name in self.macro_dict:
                                if self.macro_dict[macro_name].info.update_time < macro_record.info.update_time:
                                    self.macro_dict[macro_name] = macro_record
                                else:
                                    continue
                            else:
                                self.macro_dict[macro_name] = macro_record
                        else:
                            path_record = PathRecord.model_validate_json(json_text)
                            path_name = path_record.info.name
                            if path_name in self.path_dict:
                                if self.path_dict[path_name].info.update_time < path_record.info.update_time:
                                    self.path_dict[path_name] = path_record
                                else:
                                    continue
                            else:
                                self.path_dict[path_name] = path_record
                    except Exception as e:
                        logger.error(f"读取脚本文件{file}失败: {e}")
                        continue

    def query_path(self, path_name=None, target=None, type=None, count=None, return_one=False) -> list[PathRecord] | PathRecord | None:
        # 指定名字就直接返回单文件（用于内部固定路线的任务使用，比如每日任务）
        if path_name:
            return self.path_dict.get(path_name, None)
        
        # 根据要求进行筛选
        res = []
        for _, path_record in self.path_dict.items():
            match = True
            
            # Filter by target (exact match)
            if target is not None:
                if path_record.info.target != target:
                    match = False
            
            # Filter by type (exact match)
            if type is not None:
                if path_record.info.type != type:
                    match = False
            
            # Filter by count (greater than or equal)
            if count is not None:
                if path_record.info.count is None or path_record.info.count < count:
                    match = False
            
            if match:
                res.append(path_record)
        
        if return_one:
            return res[0] if res else None
        else:
            return res
    
    def delete_path(self, path_name: str) -> int:
        """
        删除指定名称的路线
        
        Args:
            path_name: 路线名称
            
        Returns:
            删除的文件数量，如果出错返回 0
        """
        if not path_name:
            logger.warning("Path name is empty, cannot delete")
            return 0
        
        if not os.path.exists(SCRIPT_PATH):
            logger.warning(f"Script path does not exist: {SCRIPT_PATH}")
            return 0
        
        try:
            target_filepath = []
            for file in os.listdir(SCRIPT_PATH):
                if not file.endswith(".json"):
                    continue
                
                file_path = os.path.join(SCRIPT_PATH, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            path_data = json.load(f)
                            # 检查路线名是否匹配
                            if path_data.get("info", {}).get("name") == path_name:
                                target_filepath.append(file_path)
                        except (json.JSONDecodeError, KeyError, TypeError):
                            # 跳过格式错误的文件
                            continue
                except Exception as e:
                    logger.warning(f"Failed to read file {file}: {e}")
                    continue
            
            # 删除成功后，重新初始化路径字典
            deleted_count = 0
            for file_path in target_filepath:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete file {file_path}: {e}")
                    continue
            if deleted_count > 0:
                self.init_path_dict()
                logger.info(f"Deleted {deleted_count} file(s) for path '{path_name}'")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete path '{path_name}': {e}")
            return 0

    def open_path_folder(self):
        """打开路线文件夹"""
        try:
            if os.path.exists(SCRIPT_PATH):
                os.startfile(SCRIPT_PATH)
                logger.info(f"Opened path folder: {SCRIPT_PATH}")
            else:
                return False, f"路线文件夹不存在:{SCRIPT_PATH}"
        except Exception as e:
            logger.error(f"Failed to open path folder: {e}")
            return False, f"无法打开路线文件夹:{str(e)}"
        return True, f"已打开路线文件夹:{SCRIPT_PATH}"

    def query_macro(self, macro_name) -> MacroRecord | None:
        return self.macro_dict.get(macro_name, None)

scripts_manager = ScriptsManager()