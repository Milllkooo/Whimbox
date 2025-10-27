from pydantic import BaseModel
from typing import Optional
import os

from whimbox.common.path_lib import SCRIPT_PATH
from whimbox.common.logger import logger


# 自动寻路时，当距离传送点offset内，就不传送了
# 记录路线时，当起点距离传送点offset外，就不予记录
not_teleport_offset = 15


class PathInfo(BaseModel):
    name: str   # 路径名，也是导出的json文件名
    type: Optional[str] = None   # 类型：采集、捕虫、清洁、战斗、综合
    target: Optional[str] = None # 目标：素材名
    count: Optional[int] = None # 目标数量
    region: Optional[str] = None
    map: Optional[str] = None
    update_time: Optional[str] = None
    default: Optional[bool] = None # 是否默认订阅

class PathPoint(BaseModel):
    id: int
    move_mode: str          # 移动模式：行走、跳跃、飞行
    point_type: str      # 点位类型：途径点、必经点
    action: Optional[str] = None
    action_params: Optional[str] = None
    position: list[float]

class PathRecord(BaseModel):
    info: PathInfo
    points: list[PathPoint]


class PathManager:

    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.path_dict = {}
        self.init_path_dict()

        self._initialized = True

    def init_path_dict(self):
        self.path_dict = {}
        for file in os.listdir(SCRIPT_PATH):
            if file.endswith(".json"):
                with open(os.path.join(SCRIPT_PATH, file), "r", encoding="utf-8") as f:
                    try:
                        path_record = PathRecord.model_validate_json(f.read())
                        path_name = path_record.info.name
                        if path_name in self.path_dict:
                            if self.path_dict[path_name].info.update_time < path_record.info.update_time:
                                self.path_dict[path_name] = path_record
                            else:
                                continue
                        else:
                            self.path_dict[path_name] = path_record
                    except Exception as e:
                        logger.error(f"读取路径文件{file}失败: {e}")
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

path_manager = PathManager()