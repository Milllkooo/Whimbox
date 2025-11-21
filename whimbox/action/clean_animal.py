from whimbox.interaction.interaction_core import itt
from whimbox.action.material_track_base import MaterialTrackBaseTask
from whimbox.common.utils.ui_utils import *
from whimbox.common.keybind import keybind

class CleanAnimalTask(MaterialTrackBaseTask):
    def __init__(self, animal_name, expected_count=1):
        super().__init__(animal_name, expected_count)

    # def pre_play_func(self):
    #     # 主动按F跳过清洁动画
    #     if wait_until_appear(TextFSkip):
    #         itt.key_press(keybind.KEYBIND_INTERACTION)
    
    def post_play_func(self):
        pass

if __name__ == "__main__":
    from whimbox.map.map import nikki_map
    from whimbox.view_and_move.view import calibrate_view_rotation_ratio
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CleanAnimalTask("汪汪毛线", expected_count=2)
    # task.task_run()
    task.step3()