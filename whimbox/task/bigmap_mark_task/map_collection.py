import ctypes
import json
import os
import time
import traceback
from typing import List, Dict, Set, Tuple, Optional

import numpy as np
import requests

from whimbox.common.logger import logger
from whimbox.common.path_lib import ASSETS_PATH
from whimbox.interaction.interaction_core import itt
from whimbox.map.convert import convert_GameLoc_to_PngMapPx
from whimbox.map.detection.cvars import (
    BIGMAP_POSITION_SCALE_DICT,
    GAMELOC_TO_PNGMAP_OFFSET_DICT,
    MAP_NAME_MIRALAND,
)
from whimbox.map.map import Map
from whimbox.task.task_template import (
    STATE_TYPE_ERROR,
    TaskTemplate,
    register_step,
)
from whimbox.ui.page_assets import page_bigmap, page_main
from whimbox.ui.ui import ui_control
from whimbox.ui.ui_assets import AreaBigMapTeleportButton


class MapCollectionTask(TaskTemplate):
    """
    大地图物品收集任务类。
    """

    def __init__(self):
        super().__init__("map_collection_task")
        self.map = Map()
        self.map.map_name = MAP_NAME_MIRALAND
        self.api_url = "https://myl-api.nuanpaper.com/v1/strategy/map/user/info"
        self.token_file = os.path.join(ASSETS_PATH, "token.json")
        self.assets_dir = os.path.join(ASSETS_PATH, "map_position")
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen_center = (960, 540)

    @register_step("进入大地图")
    def step1(self):
        ui_control.goto_page(page_bigmap)
        # 尝试定位
        self.map.get_bigmap_posi()
        if self.map.bigmap_similarity < 0.3:
            msg = f"大地图匹配相似度较低 ({self.map.bigmap_similarity:.2f})，请确认是否已打开大地图。"
            self.update_task_result(status=STATE_TYPE_ERROR, message=msg)
            return "step3"  # 直接跳到结束

        return "step2"

    @register_step("执行收集")
    def step2(self):
        return self.execute_collection()

    def get_acquired_ids(self) -> Set[str]:
        """
        从API获取已获得的物品ID，使用token.json中的凭据。
        """
        if not os.path.exists(self.token_file):
            logger.error(f"令牌文件未找到: {self.token_file}")
            return set()

        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                creds = json.load(f)

            # 处理可能的嵌套结构
            if "user_map" in creds:
                creds = creds["user_map"]

            token = creds.get("token")
            openid = creds.get("openid")

            if not token or not openid:
                logger.error("token.json 中缺少 token 或 openid")
                return set()

            payload = {"client_id": 1106, "token": token, "openid": openid}

            logger.info(f"正在从 {self.api_url} 请求用户信息...")
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            items_data = data.get("data")
            if items_data is None:
                logger.warning("在 API 响应中找不到 'data' 列表或格式未知。")
                logger.debug(f"响应: {data}")
                return set()

            acquired_ids = set()

            def extract_ids(items):
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and "id" in item:
                            acquired_ids.add(str(item["id"]))
                        elif isinstance(item, (str, int)):
                            acquired_ids.add(str(item))
                elif isinstance(items, dict):
                    for value in items.values():
                        extract_ids(value)

            extract_ids(items_data)

            logger.info(f"已获取 {len(acquired_ids)} 个已获得物品。")
            return acquired_ids

        except Exception as e:
            logger.error(f"获取已获得 ID 时出错: {e}")
            return set()

    def load_and_filter_items(
        self, acquired_ids: Set[str], world_id: str = "1"
    ) -> List[Dict]:
        """
        从 JSON 文件加载物品，并过滤掉已获得的物品和不在当前世界中的物品。
        world_id 默认是 1。
        """
        target_files = ["star.json", "dewdrop.json", "box.json"]
        # 其他可能的点位文件: "cruise.json", "read.json"

        all_items = []

        for filename in target_files:
            filepath = os.path.join(self.assets_dir, filename)
            if not os.path.exists(filepath):
                logger.warning(f"物品文件未找到: {filepath}")
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    items = json.load(f)

                count = 0
                for item in items:
                    # 按 world_id 过滤
                    if str(item.get("world_id", "")) != world_id:
                        continue

                    # 按已获得状态过滤
                    item_id = str(item.get("id", ""))
                    if item_id in acquired_ids:
                        continue

                    # 过滤掉没有 text 属性或 text 为空的点，因为这些点可能没在大地图上
                    if not item.get("text"):
                        continue

                    # 添加类型用于调试/日志记录
                    item["type"] = filename.replace(".json", "")
                    all_items.append(item)
                    count += 1

                logger.info(f"从 {filename} 加载了 {count} 个未获得的物品。")

            except Exception as e:
                logger.error(f"加载 {filename} 时出错: {e}")

        return all_items

    def calculate_screen_pos(
        self, item_loc: List[float], center_pos: Tuple[float, float]
    ) -> Optional[Tuple[int, int]]:
        """
        将物品的游戏位置转换为屏幕坐标。
        如果超出屏幕，则返回 None。
        """
        try:
            # 1. 游戏位置 -> Png 地图像素
            points = np.array(item_loc[:2])  # 只需要 x, y
            png_px = convert_GameLoc_to_PngMapPx(points, map_name=self.map.map_name)

            offset = GAMELOC_TO_PNGMAP_OFFSET_DICT.get(self.map.map_name, (0, 0))
            png_px[0] -= offset[0]
            png_px[1] -= offset[1]

            # 2. 获取缩放比例 (PNG -> 游戏内大地图)
            scale = BIGMAP_POSITION_SCALE_DICT.get(self.map.map_name, 1.0)

            item_ingame_px = png_px / scale
            center_ingame_px = np.array(center_pos) / scale

            screen_x = int(
                item_ingame_px[0] - center_ingame_px[0] + self.screen_center[0]
            )
            screen_y = int(
                item_ingame_px[1] - center_ingame_px[1] + self.screen_center[1]
            )

            # 3. 可见性检查
            if 0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height:
                return (screen_x, screen_y)

            return None

        except Exception as e:
            logger.error(f"计算坐标时出错: {e}")
            return None

    def execute_collection(self):
        """
        主执行方法。
        """
        # 1. 获取已获得的 ID
        acquired_ids = self.get_acquired_ids()
        if not acquired_ids:
            logger.warning("未找到已获得的 ID。")

        # 2. 加载物品
        items = self.load_and_filter_items(acquired_ids)
        if not items:
            logger.info("未找到未获得的物品。")
            self.update_task_result(message="未找到未获得的物品。")
            return "step3"

        center_pos = self.map.get_bigmap_posi()
        logger.info(f"当前大地图中心: {center_pos}")

        # 3. 迭代并收集
        collected_count = 0
        processed_positions = []
        cluster_threshold = 4  # 簇阈值，太近的点位跳过

        for item in items:
            if self.need_stop():
                break

            coords = item.get("coordinates")
            if not coords:
                continue

            screen_pos = self.calculate_screen_pos(coords, center_pos)
            if not screen_pos:
                continue

            # 检查是否与已处理的点过于接近（簇）
            is_close = any(
                ((screen_pos[0] - ep[0]) ** 2 + (screen_pos[1] - ep[1]) ** 2) ** 0.5
                < cluster_threshold
                for ep in processed_positions
            )

            if is_close:
                logger.debug(f"物品 {item.get('id')} 距离太近，跳过。")
                continue

            processed_positions.append(screen_pos)
            logger.info(f"找到可见物品 {item.get('id')} ({item.get('type')}) 在 {screen_pos}")

            itt.move_and_click(screen_pos, type="right")
            time.sleep(0.5)  # 等待 UI 响应

            # 检查确认按钮
            try:
                button_text = itt.ocr_single_line(AreaBigMapTeleportButton)
                logger.info(f"OCR 结果: {button_text}")

                if "确认" in button_text:
                    logger.info("找到确认。点击...")
                    AreaBigMapTeleportButton.click()
                    time.sleep(0.3)
                    collected_count += 1
                else:
                    logger.info(f"文本 '{button_text}' 与 '确认' 不匹配。跳过。")

            except Exception as e:
                logger.error(f"交互过程中出错: {e}")

        msg = f"收集任务完成。尝试标记了 {collected_count} 个点位。"
        logger.info(msg)
        self.update_task_result(message=msg)
        return "step3"

    @register_step("退出")
    def step3(self):
        ui_control.goto_page(page_main)


if __name__ == "__main__":
    # 手动启用 DPI 感知
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

    logger.info("正在初始化截图...")

    task = MapCollectionTask()

    try:
        task.task_run()
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        traceback.print_exc()