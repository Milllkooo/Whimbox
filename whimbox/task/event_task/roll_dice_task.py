"""
1.11版本大富翁，自动抛骰子搓核弹
"""

from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import *
from whimbox.common.utils.ui_utils import *
from whimbox.common.logger import logger
from whimbox.common.timer_module import AdvanceTimer

question_answer_dict = {
    "不属于花园镇的搭配团": "美妆搭配团",
    "存愿望瓶的地方": "愿望梦境仓库",
    "大许愿树上悬挂的许愿道具中没有以下哪种": "愿望风铃",
    "大喵最喜欢吃什么": "五花肉",
    "带我逆流，带我逆流": "蓝眼泪",
    "女王行宫遗迹内部有个中央花坛": "小提琴",
    "服装升级不需要": "怦然思绪",
    "花愿镇搭配师协会的管理者是谁": "达达",
    "纪念公园的雕像缺了哪个部位": "头部",
    "假如毛毛的妈妈": "毛毛",
    "巨蛇遗迹位于哪个区域": "微风绿野",
    "灵感露珠是哪个族群的灵感来源": "唱诗蓝龙",
    "美鸭梨最多": "4",
    "民俗手册的研发者叫什么名字": "塞吉托",
    "哪一种花朵只在雨天出现": "雨滴蝶兰",
    "暖暖家园里的舒适大床": "48.1",
    "哪位是最喜欢猜谜游戏的心愿精灵": "嘟嘟利达",
    "哪位曙光骑士在古铸剑遗址留下了遗言": "赫尔塔",
    "能够把人弹到更高地方的动物叫什么": "弹射海豹",
    "祈愿树林的圣地花谷": "金蔷薇",
    "如果想要往返于高大的石树之间": "飞花滑翔",
    "如何快速定位奇想星的位置": "大喵视野",
    "谁曾担任过愿望大师": "奇格格达",
    "谁曾是涟漪之窖的主人": "涟漪岁月",
    "帮助我们快速传递于地图之间": "流转之柱",
    "但最多只有一个": "你的影子",
    "什么卸妆水最滑": "滑溜溜卸妆水",
    "什么东西越热它爬得越高": "温度计里的水银柱",
    "什么字所有人都会念错": "错",
    "石树田无人区最高点在哪": "石之冠",
    "手套女士最后的名字": "罗丝妮丝",
    "缇米丝研发的什么东西": "超畅爽卸妆油",
    "弹射海豹最喜欢吃什么": "奇想鱼干",
    "微光水潭有什么鱼": "蝴蝶结鱼",
    "哪个节日共燃愿望": "火冠节",
    "小石树田村染织工坊主兼村民自洽会": "司本多",
    "小石树田村最高的地方在哪里": "石之冠",
    "心愿精灵通过哪种奇想道具": "愿望扩音喇叭",
    "星海里没有什么": "星光果",
    "星之海套装共有几个部件": "7",
    "以下哪个区域不属于石树田无人区": "花树高地",
    "以下哪位是远近闻名的美妆商人": "缇米丝",
    "以下哪项不是家园园宝的名字": "喵园园",
    "以下哪项不是解锁虹染色盘的道具": "幻梦棱镜",
    "以下哪种鱼不会出现在花园镇": "眼影鱼",
    "以下哪种鱼不是小石树田村的鱼类": "缎带鱼",
    "以下哪个不是祈愿树林的特殊产物": "噼啪花粉",
    "以下哪个搭配师团不属于祈愿树林": "好绿野搭配师团",
    "以下哪种生物会出现在石树田无人区": "巡星天鹅",
    "以下谁不是搭配天王": "乔万尼",
    "愿望梦境仓库有几座": "3",
    "愿望球有哪几个": "绝望球",
    "有了美鸭梨": "搭配没压力",
    "祝福闪光有几种部件": "3",
    "祝福闪光的部位不包括": "腰部",
}

position_step_dict = {
    (990, 570): 6,
    (1124, 489): 5,
    (1258, 409): 4,
    (1393, 373): 3,
    (1527, 373): 2,
    (1661, 373): 1,
}

rotate_dice_position = (1498, 973)
main_control_dice_position = (1811, 816)
control_dice_position_dict = {
    1: (1512, 555),
    2: (1640, 555),
    3: (1767, 555),
    4: (1512, 660),
    5: (1640, 660),
    6: (1767, 660),
}

def find_arrows(cap):
    arrows = []
    if CV_DEBUG_MODE:
        cap_copy = cap.copy()
    lower = [35, 15, 250]
    upper = [50, 20, 255]
    img = process_with_hsv_limit(cap, lower, upper)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            continue
        m = cv2.moments(contour)
        if m['m00'] != 0:
            cx = int(m['m10']/m['m00'])
            cy = int(m['m01']/m['m00'])
            arrows.append((cx, cy))
    if CV_DEBUG_MODE and len(arrows) != 0:
        for arrow in arrows:
            cv2.circle(cap_copy, arrow, 5, (0, 0, 255), 2)
        cv2.imshow("img", cap_copy)
        cv2.waitKey(0)
    return arrows

def choose_arrow(arrows):
    # 尽可能选择左下的箭头
    target_arrow = None
    arrow1 = arrows[0]
    arrow2 = arrows[1]
    # 在同一垂直线上，取下面的箭头
    if abs(arrow1[0]-arrow2[0]) < 5:
        if arrow1[1] < arrow2[1]:
            target_arrow = arrow2
        else:
            target_arrow = arrow1
    # 在同一水平线上，取左边的箭头
    elif abs(arrow1[1]-arrow2[1]) < 5:
        if arrow1[0] < arrow2[0]:
            target_arrow = arrow1
        else:
            target_arrow = arrow2
    # 在对角线上，取下面的箭头
    else:
        if arrow1[1] < arrow2[1]:
            target_arrow = arrow2
        else:
            target_arrow = arrow1
    return target_arrow

class RollDiceTask(TaskTemplate):
    def __init__(self):
        super().__init__("roll_dice_task")
        self.random_dice_num = 0
        self.rotate_dice_num = 0
        self.control_dice_num = 0
        self.min_dice_num = 5
        self.in_loop_position = False
        self.direction = None
        self.loop_position = None

    def check_can_play(self):
        cap = itt.capture(posi=AreaMonopolyDiceNum.position)
        lower = [0, 0, 240]
        upper = [180, 255, 255]
        px_count = count_px_with_hsv_limit(cap, lower, upper)
        if px_count > 500:
            return True
        else:
            return False

    def play_random_dice(self):
        if self.random_dice_num > self.min_dice_num:
            self.log_to_gui(f"扔普通骰子")
            self.random_dice_num -= 1
            itt.move_and_click(ButtonMonopolyRollDice.click_position())
            time.sleep(0.5)
            return True
        else:
            return False
    
    def play_rotate_dice(self):
        if self.rotate_dice_num > self.min_dice_num:
            self.log_to_gui(f"扔旋转骰子")
            self.rotate_dice_num -= 1
            itt.move_and_click(rotate_dice_position)
            time.sleep(0.8)
            if self.direction == "left":
                self.direction = "right"
            elif self.direction == "right":
                self.direction = "left"
            return True
        else:
            self.in_loop_position = False
            return False
    
    def play_control_dice(self, target_step):
        if self.control_dice_num > self.min_dice_num:
            self.log_to_gui(f"扔随心骰子{target_step}点")
            self.control_dice_num -= 1
            itt.move_and_click(main_control_dice_position)
            time.sleep(0.3)
            control_dice_position = control_dice_position_dict[target_step]
            itt.move_and_click(control_dice_position)
            time.sleep(0.5)
            return True
        else:
            self.in_loop_position = False
            return False
    
    def skip_play(self):
         # 通过esc返回再进入，快速跳过走路过程
        itt.key_press('esc')
        wait_until_appear_then_click(ButtonMonopolyEntrance)
        itt.wait_until_stable(threshold=0.9, timeout=2)

    def check_and_choose_arrow(self):
        arrows = find_arrows(itt.capture())
        if len(arrows) == 2:
            logger.info(f"经过岔路, {arrows}")
            target = choose_arrow(arrows)
            itt.move_and_click(target)
            time.sleep(0.5)
            self.skip_play()
            return True
        else:
            return False

    def check_in_loop_position(self):
        cap = itt.capture()
        rate, loc = similar_img(cap, IconMonopolyMapFeature2.image, ret_mode=IMG_RECT)
        logger.info(f"检查是否在左下角双问号处, rate: {rate}, loc: {loc}")
        if rate > 0.99 and loc[1] < 3 and self.loop_position != None and self.in_loop_position:
            return True
        else:
            self.loop_position = None
            self.in_loop_position = False
            return False

    # 前往左下角双问号处
    def goto_loop_position(self):
        cap = itt.capture()
        cap_copy = cap.copy()
        rate, loc = similar_img(cap_copy, IconMonopolyMapFeature.image, ret_mode=IMG_RECT)
        # 根据参照物，判断当前位置是否在左下角附近
        if rate < 0.99:
            return False
        target_step = 0
        for position, step in position_step_dict.items():
            if position[0]-5<loc[0]<position[0]+5 and position[1]-5<loc[1]<position[1]+5:
                target_step = step
                break
        if target_step == 0:
            return False

        #成功发现在左下角附近，判断朝向
        cap_copy = cap.copy()
        feature_left = IconMonopolyNikkiFeature.image
        feature_right = cv2.flip(IconMonopolyNikkiFeature.image, 1)
        rate_left, loc_left = similar_img(cap_copy, feature_left, ret_mode=IMG_RECT)
        rate_right, loc_right = similar_img(cap_copy, feature_right, ret_mode=IMG_RECT)
        if rate_left > rate_right and rate_left > 0.99:
            self.direction = "left"
        elif rate_right > rate_left and rate_right > 0.99:
            self.direction = "right"
        
        if self.direction == None:
            return False
        # 如果面朝右就旋转
        if self.direction == "right":
            if not self.play_rotate_dice():
                return False
        if not self.play_control_dice(target_step):
            return False
        self.skip_play()
        self.in_loop_position = True
        self.loop_position = "right"
        return True


    @register_step("进入核弹制造页面")
    def step1(self):
        ui_control.goto_page(page_event)
        wait_until_appear_then_click(ButtonMonopolyEntrance)
        itt.wait_until_stable(threshold=0.90, timeout=2)
        # 领取每日奖励
        wait_until_appear_then_click(ButtonMonopolyConfirmDailyAward)
        # 关闭弹幕
        if itt.get_img_existence(ButtonMonopolySendBullet):
            itt.move_and_click(ButtonMonopolyCloseBullet.click_position())
        if not self.check_can_play():
            self.task_stop(message="骰子不可交互，请先手动完成进行中的事件")
            return
        # 获取骰子数量
        max_try = 3
        while max_try > 0:
            dice_num_texts = itt.ocr_multiple_lines(AreaMonopolyDiceNum)
            if len(dice_num_texts) != 4 and dice_num_texts[1] != "随心":
                max_try -= 1
                continue
            self.control_dice_num = int(dice_num_texts[0])
            self.random_dice_num = int(dice_num_texts[2])
            self.rotate_dice_num = int(dice_num_texts[3])
            break
        if max_try == 0:
            raise Exception("骰子数量获取异常")
        else:
            self.log_to_gui(f"基础骰子x{self.random_dice_num},旋转骰子x{self.rotate_dice_num},随心骰子x{self.control_dice_num}")


    @register_step("开始抛骰子")
    def step2(self):
        # 等待骰子按钮可交互
        while not self.check_can_play() and not self.need_stop():
            logger.info("等待骰子按钮可交互")
            time.sleep(0.5)
        # 先判断能否前往双问号处，能去就直接去
        if self.goto_loop_position():
            return
        # 判断当前是否在双问号处
        self.in_loop_position = self.check_in_loop_position()
        # 判断并前往左下角双问号处
        if not self.in_loop_position:
            # 如果不处于刷问号阶段，就扔普通骰子
            if not self.play_random_dice():
                return 'step4'
            # 如果已经在岔路，需要立刻点击箭头
            if not self.check_and_choose_arrow():
                self.skip_play()
            while True:
                if not self.check_and_choose_arrow():
                    break
        else:
            # 如果处于刷问号阶段，就开刷
            if self.loop_position == "right" and self.direction == "left":
                self.play_control_dice(1)
                self.skip_play()
                self.loop_position = "left"
            elif self.loop_position == "right" and self.direction == "right":
                self.play_rotate_dice()
                self.play_control_dice(1)
                self.skip_play()
                self.loop_position = "left"
            elif self.loop_position == "left" and self.direction == "left":
                self.play_rotate_dice()
                self.play_control_dice(1)
                self.skip_play()
                self.loop_position = "right"
            elif self.loop_position == "left" and self.direction == "right":
                self.play_control_dice(1)
                self.skip_play()
                self.loop_position = "right"

    
    def handle_question(self):
        self.log_to_gui("处理事件：答题")
        itt.move_and_click(ButtonMonopolyStartQuestion.click_position())
        time.sleep(0.3)
        success = False
        question = itt.ocr_single_line(AreaMonopolyQuestion)
        answers = itt.ocr_and_detect_posi(AreaMonopolyAnswer)
        logger.info(f"问题: {question}, 答案: {answers}")
        for q in question_answer_dict:
            if q in question:
                a = question_answer_dict[q]
                for answer_text, answer_box in answers.items():
                    if a in answer_text:
                        center = area_center(answer_box)
                        click_posi = (
                            AreaMonopolyAnswer.position[0] + center[0], 
                            AreaMonopolyAnswer.position[1] + center[1]
                        )
                        itt.move_and_click(click_posi)
                        success = True
                        break
                break
        if not success:
            itt.move_and_click(AreaMonopolyAnswer.center_position())
        itt.delay(0.5, comment="等待答题后摇")

    def handle_ticket(self):
        self.log_to_gui("处理事件：刮刮乐")
        click_positions = [(820, 430), (962, 585), (1106, 724)]
        for click_position in click_positions:
            itt.move_and_click(click_position)
            time.sleep(0.3)
        itt.delay(3, comment="等待刮刮乐后摇")

    def handle_fun_box(self):
        self.log_to_gui("处理事件：玩趣箱")
        options = itt.ocr_and_detect_posi(AreaMonopolyFunboxOptions)
        logger.info(f"玩趣箱选项: {options}")
        target_box = None
        for option, box in options.items():
            if "单次上限" in option or "下一次注入灵感" in option:
                target_box = box
                break
        if target_box:
            timer = AdvanceTimer(5).start()
            while True:
                if timer.reached():
                    logger.info("玩趣箱选项超时")
                    break
                img = itt.capture(posi=AreaMonopolyFunboxOptions.position)
                lower = [0, 150, 250]
                upper = [180, 200, 255]
                img = process_with_hsv_limit(img, lower, upper)
                contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(contours) == 1:
                    rect = cv2.minAreaRect(contours[0])
                    center_x = int(rect[0][0])
                    center_y = int(rect[0][1])
                    # 如果框落在目标选项内，就停止
                    if center_x > target_box[0] and center_x < target_box[2] and center_y > target_box[1] and center_y < target_box[3]:
                        itt.delay(0.1, comment=f"找到目标选项:{option},稍等片刻再点停")
                        itt.move_and_click(ButtonMonopolyStopFunBox.click_position())
                        break
                time.sleep(0.05)
        else:
            # 没有目标选项，就随便停一个
            itt.move_and_click(ButtonMonopolyStopFunBox.click_position())
        itt.delay(2, comment="等待玩趣箱后摇")


    @register_step("处理事件")
    def step3(self):
        need_skip_play = False
        # 玩趣箱
        if itt.get_img_existence(ButtonMonopolyStopFunBox):
            self.handle_fun_box()
            need_skip_play = True
        # 新鲜事
        elif itt.get_img_existence(ButtonMonopolyConfirmEvent):
            self.log_to_gui("处理事件：新鲜事")
            itt.move_and_click(ButtonMonopolyConfirmEvent.click_position())
            itt.delay(1, comment="等待新鲜事后摇")
            need_skip_play = True
        # 离开格子
        elif itt.get_img_existence(ButtonMonopolyLeaveGrid):
            self.log_to_gui("处理事件：离开格子")
            itt.move_and_click(ButtonMonopolyLeaveGrid.click_position())
        # 答题
        elif itt.get_img_existence(ButtonMonopolyStartQuestion):
            self.handle_question()
        # 刮刮乐
        elif itt.get_img_existence(IconMonopolyTicketFeature):
            self.handle_ticket()
        # 任务已满
        elif itt.get_img_existence(ButtonMonopolyTaskFull):
            self.log_to_gui("处理事件：随机任务已满")
            itt.move_and_click(ButtonMonopolyTaskFull.click_position())
        
        if need_skip_play:
            self.skip_play()
            while True:
                if not self.check_and_choose_arrow():
                    break
        return 'step2'

    @register_step("搓核弹结束")
    def step4(self):
        return


if __name__ == "__main__":
    roll_dice_task = RollDiceTask()
    roll_dice_task.task_run()

    # import os
    # from whimbox.common.path_lib import *
    # org = cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763252877.5653985.png"))
    # img = crop(org, AreaMonopolyFunboxOptions.position)
    # img_copy = img.copy()
    # lower = [0, 150, 250]
    # upper = [180, 200, 255]
    # img = process_with_hsv_limit(img, lower, upper)
    # contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # if len(contours) == 1:
    #     rect = cv2.minAreaRect(contours[0])
    #     center_x = int(rect[0][0])
    #     center_y = int(rect[0][1])
    #     print(f"center_x: {center_x}, center_y: {center_y}")
    #     cv2.circle(img_copy, (center_x, center_y), 5, (0, 0, 255), 2)
    #     cv2.imshow("img", img_copy)
    #     cv2.waitKey(0)

    # while True:
    #     input('enter to capture') 
    #     cap = itt.capture()
    #     cap_copy = cap.copy()
    #     rate, loc = similar_img(cap, IconMonopolyNikkiFeature.image, ret_mode=IMG_RECT)
    #     print(rate, loc)
    #     cv2.rectangle(cap_copy, loc, (loc[0]+IconMonopolyNikkiFeature.image.shape[1], loc[1]+IconMonopolyNikkiFeature.image.shape[0]), (0, 0, 255), 2)
    #     feature = cv2.flip(IconMonopolyNikkiFeature.image, 1)
    #     rate, loc = similar_img(cap, feature, ret_mode=IMG_RECT)
    #     print(rate, loc)
    #     cv2.rectangle(cap_copy, loc, (loc[0]+feature.shape[1], loc[1]+feature.shape[0]), (0, 255, 0), 2)
    #     cv2.imshow("img", cap_copy)
    #     cv2.waitKey(0)

    # while True:
    #     input('enter to capture')
    #     cap = itt.capture()
    #     rate, loc = similar_img(cap, IconMonopolyMapFeature2.image, ret_mode=IMG_RECT)
    #     print(rate, loc)

    # import os
    # from whimbox.common.path_lib import *
    # # cap = cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763299021.5629537.png"))
    # # cap = crop(cap, AreaMonopolyDiceNum.position)
    # # lower = [0, 0, 240]
    # # upper = [180, 255, 255]
    # # print(count_px_with_hsv_limit(cap, lower, upper))

    # cap = cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763253146.1713786.png"))
    # arrows = find_arrows(cap)
    # target_arrow = choose_arrow(arrows)
    # print(target_arrow)