from whimbox.interaction.interaction_core import itt
from whimbox.action.material_track_base import MaterialTrackBaseTask
from whimbox.common.utils.ui_utils import *

class CatchInsectTask(MaterialTrackBaseTask):
    def __init__(self, insect_name, expected_count=1):
        super().__init__(insect_name, expected_count)

    def pre_play_func(self):
        pass

    def post_play_func(self):
        time.sleep(0.8) # 等待捕虫动作结束


if __name__ == "__main__":
    from whimbox.map.map import nikki_map
    from whimbox.view_and_move.view import calibrate_view_rotation_ratio
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CatchInsectTask("发卡蚱蜢", 3)
    # task.task_run()
    task.step3()