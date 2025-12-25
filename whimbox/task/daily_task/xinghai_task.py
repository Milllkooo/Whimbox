"""
检查并领取星海日常
"""

from whimbox.task.task_template import *
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.common.utils.ui_utils import *
from whimbox.task.daily_task.cvar import *
from whimbox.common.logger import logger
from whimbox.map.map import nikki_map
from whimbox.map.convert import convert_GameLoc_to_PngMapPx
from whimbox.map.detection.cvars import MAP_NAME_STARSEA
from whimbox.task.daily_task.lookbook_like_task import LookbookLikeTask
from whimbox.task.daily_task.xinghai_group_chat_task import XinghaiGroupChatTask

xhsg_task_info_list = [
    {
        "key_words": ["摆饰"],
        "score": 200,
        "priority": 5,
        "task_name": XHSG_TASK_PLACE_ITEM
    },
    {
        "key_words": ["聚会频道"],
        "score": 100,
        "priority": 5,
        "task_name": XHSG_TASK_GROUP_CHAT
    },
    {
        "key_words": ["星绘图册", "点赞"],
        "score": 200,
        "priority": 5,
        "task_name": XHSG_TASK_BOOKLOOK_LIKE
    },
    {
        "key_words": ["椰果采摘"],
        "score": 300,
        "priority": 0,
        "task_name": XHSG_TASK_COCO_PICKUP
    },
    {
        "key_words": ["举起椰", "照片"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_COCO_PHOTO
    },
    {
        "key_words": ["星愿碎片", "投递"],
        "score": 300,
        "priority": 0,
        "task_name": XHSG_TASK_JAR_PICKUP
    },
    {
        "key_words": ["星愿碎片", "照片"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_JAR_PHOTO
    },
    {
        "key_words": ["10个星光结晶"],
        "score": 100,
        "priority": 0,
        "task_name": XHSG_TASK_STAR_PICKUP
    },
    {
        "key_words": ["1次流星"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_METEOR
    },
    {
        "key_words": ["星芒之翼", "合影"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_PLANE_PHOTO
    },
    {
        "key_words": ["漂流瓶", "查看"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_BOTTLE_PICKUP
    },
    {
        "key_words": ["制造", "泡泡"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_BUBBLE_MAKE
    },
    {
        "key_words": ["泡泡", "合影"],
        "score": 200,
        "priority": 0,
        "task_name": XHSG_TASK_BUBBLE_PHOTO
    },
]

class XinghaiTask(TaskTemplate):
    def __init__(self):
        super().__init__("xinghai_task")
        self.current_score = 0
        self.todo_list = []

    @register_step("传送到星海无界枢纽")
    def step0(self):
        map_loc = convert_GameLoc_to_PngMapPx([-35070.57421875, 44421.59765625], MAP_NAME_STARSEA)
        nikki_map.bigmap_tp(map_loc, MAP_NAME_STARSEA)
    
    @register_step("摇铃")
    def step1(self):
        itt.key_down(keybind.KEYBIND_BELL)
        time.sleep(3)
        itt.key_up(keybind.KEYBIND_BELL)
        wait_until_appear(IconPageMainFeature, 10)

    @register_step("检查星海拾光完成情况")
    def step2(self):
        ui_control.goto_page(page_xhsg) 
        try:
            itt.wait_until_stable(threshold=0.95)
            score_str = itt.ocr_single_line(AreaXhsgScore)
            score = int(score_str.strip())
            if score % 100 != 0:
                raise Exception(f"星海拾光分数识别异常:{score_str}")
        except:
            raise Exception(f"星海拾光分数识别异常:{score_str}")
        self.current_score = score
        if score == 500:
            return "step5"
        else:
            self.log_to_gui(f"星海拾光完成度：{score}/500")
            return "step3"

    @register_step("查看星海拾光具体任务")
    def step3(self):
        def check_task(task_btn: Button):
            task_btn.click()
            time.sleep(0.3)
            if not itt.get_img_existence(IconXhsgTaskFinished):
                task_text = itt.ocr_single_line(AreaXhsgTaskText)
                logger.info(f"任务文本：{task_text}")
                for task_info in xhsg_task_info_list:
                    is_match = True
                    for key_word in task_info["key_words"]:
                        if key_word not in task_text:
                            is_match = False
                            break
                    if is_match:
                        return task_info
                return None
            else:
                return None

        # 获得未完成任务列表
        unfinished_task_list = []
        button_list = [ButtonZxxyTask1, ButtonZxxyTask2, ButtonZxxyTask3, ButtonZxxyTask4, ButtonZxxyTask5]
        for i in range(5):
            if self.need_stop():
                break
            unfinished_task = check_task(button_list[i])
            if unfinished_task == None:
                continue
            else:
                self.log_to_gui(f"未完成任务：{unfinished_task['task_name']}")
                unfinished_task_list.append(unfinished_task)
        
        # 根据优先级和分数，判断应该做什么任务
        temp_score = self.current_score
        unfinished_task_list.sort(
            key=lambda x: (x['priority'], x['score']),
            reverse=True
        )

        # 根据分数和优先级完成其他任务
        for task in unfinished_task_list:
            if task['priority'] == 0:
                continue
            if temp_score >= 500:
                break
            self.todo_list.append(task['task_name'])
            temp_score += task['score']
        
        if len(self.todo_list) > 0:
            self.log_to_gui(f"需要继续完成以下任务：{", ".join(self.todo_list)}")
            return
        else:
            if self.current_score < 500:
                self.log_to_gui("没办法凑齐分数了", is_error=True)
                return "step5"

    @register_step("开始做星海拾光任务")
    def step4(self):
        task_dict = {
            XHSG_TASK_BOOKLOOK_LIKE: LookbookLikeTask(),
            XHSG_TASK_GROUP_CHAT: XinghaiGroupChatTask(),
        }
        for task_name in self.todo_list:
            if task_name in task_dict:
                task = task_dict[task_name]
                task.task_run()

    @register_step("领取星海拾光奖励")
    def step5(self):
        pass

    @register_step("退出星海拾光")
    def step6(self):
        ui_control.goto_page(page_main)

if __name__ == "__main__":
    xinghai_task = XinghaiTask()
    # xinghai_task.task_run()
    xinghai_task.step0()