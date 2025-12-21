'''朝夕心愿一条龙'''

from whimbox.task.task_template import *
from whimbox.task import daily_task
from whimbox.task.navigation_task.auto_path_task import AutoPathTask
from whimbox.task.photo_task.daily_photo_task import DailyPhotoTask
from whimbox.config.config import global_config
from whimbox.task.daily_task.cvar import *
from whimbox.task.common_task.start_game_task import StartGameTask
from whimbox.map.detection.cvars import MAP_NAME_MIRALAND, MAP_NAME_UNSUPPORTED
from whimbox.map.convert import convert_GameLoc_to_PngMapPx


class AllInOneTask(TaskTemplate):
    def __init__(self):
        super().__init__("all_in_one_task")
        self.zhaoxi_todo_list = []
        self.task_result_list = {
            'dig_task': False,
            'weekly_realm_task': False,
            'zhaoxi_task': False,
            'monthly_pass_task': False,
            'energy_cost_task': False,
        }

    @register_step("自动启动游戏")
    def step0(self):
        start_game_task = StartGameTask()
        task_result = start_game_task.task_run()
        if task_result.status == STATE_TYPE_SUCCESS:
            self.log_to_gui(task_result.message)
            return "step1"
        else:
            self.log_to_gui(task_result.message, is_error=True)
            return STEP_NAME_FINISH

    @register_step("美鸭梨挖掘")
    def step1(self):
        dig_task = daily_task.DigTaskV2()
        task_result = dig_task.task_run()
        self.task_result_list['dig_task'] = task_result.data

    @register_step("检查周本进度")
    def step2(self):
        self.log_to_gui("检查是否在家园")
        from whimbox.map.map import nikki_map
        nikki_map.reinit_smallmap()
        # 如果在不支持的地图（比如家园），就传送到花愿镇
        if nikki_map.map_name == MAP_NAME_UNSUPPORTED:
            loc = convert_GameLoc_to_PngMapPx([-13172.34765625, -54273.6171875], MAP_NAME_MIRALAND)
            nikki_map.bigmap_tp(loc, MAP_NAME_MIRALAND)
        weekly_realm_task = daily_task.WeeklyRealmTask()
        task_result = weekly_realm_task.task_run()
        self.task_result_list['weekly_realm_task'] = task_result.data

    @register_step("检查朝夕心愿进度")
    def step3(self):
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        self.zhaoxi_todo_list = task_result.data
        if task_result.status == STATE_TYPE_SUCCESS:
            if not self.zhaoxi_todo_list:
                self.task_result_list['zhaoxi_task'] = True
                return "step5"
            self.log_to_gui(task_result.message)
        else:
            self.log_to_gui(task_result.message, is_error=True)
            return "step5"

    @register_step("开始完成朝夕心愿任务")
    def step4(self):
        task_dict = {
            DAILY_TASK_PICKUP: AutoPathTask(path_name="朝夕心愿_采集", excepted_num=5),
            DAILY_TASK_CATCH_INSECT: AutoPathTask(path_name="朝夕心愿_捕虫", excepted_num=3),
            DAILY_TASK_MINIGAME: AutoPathTask(path_name="朝夕心愿_小游戏"),
            DAILY_TASK_GET_BLESS: daily_task.BlessTask(),
            DAILY_TASK_JIHUA: daily_task.JihuaTask(),
            DAILY_TASK_MONSTER: daily_task.MonsterTask(),
            DAILY_TASK_TAKE_PHOTO: DailyPhotoTask(),
        }
        for task_name in self.zhaoxi_todo_list:
            if task_name in task_dict:
                task = task_dict[task_name]
                task.task_run()
        
    @register_step("消耗剩余体力")
    def step5(self):
        energy_cost = global_config.get("Game", "energy_cost")
        if energy_cost == "素材激化幻境":
            if DAILY_TASK_JIHUA not in self.zhaoxi_todo_list:
                task = daily_task.JihuaTask()
                task.task_run()
            self.task_result_list['energy_cost_task'] = True
        elif energy_cost == "祝福闪光幻境":
            if DAILY_TASK_GET_BLESS not in self.zhaoxi_todo_list:
                task = daily_task.BlessTask()
                task.task_run()
            self.task_result_list['energy_cost_task'] = True
        elif energy_cost == "魔物试炼幻境":
            if DAILY_TASK_MONSTER not in self.zhaoxi_todo_list:
                task = daily_task.MonsterTask()
                task.task_run()
            self.task_result_list['energy_cost_task'] = True
        else:
            self.log_to_gui("未配置默认消耗体力方式")
            self.task_result_list['energy_cost_task'] = False
        
        # 如果之前朝夕心愿已经都完成了，就直接去奇迹之旅
        if not self.zhaoxi_todo_list:
            return "step7"
        else:
            return "step6"
    
    @register_step("获取朝夕心愿奖励")
    def step6(self):
        if self.task_result_list['zhaoxi_task'] == True:
            self.log_to_gui("朝夕心愿已完成，无需再次领取奖励")
            return
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        self.zhaoxi_todo_list = task_result.data
        if not self.zhaoxi_todo_list:
            self.task_result_list['zhaoxi_task'] = True
        else:
            self.task_result_list['zhaoxi_task'] = False

    @register_step("领取奇迹之旅奖励")
    def step7(self):
        monthly_pass_task = daily_task.MonthlyPassTask()
        monthly_pass_task.task_run()
        self.task_result_list['monthly_pass_task'] = True

    @register_step("一条龙结束")
    def step8(self):
        msg = ""
        if self.task_result_list['dig_task']:
            msg += "美鸭梨挖掘成功,"
        else:
            msg += "美鸭梨挖掘还无法收获,"
        if self.task_result_list['weekly_realm_task']:
            msg += "每周幻境已完成,"
        else:
            msg += "每周幻境未完成,"
        if self.task_result_list['zhaoxi_task']:
            msg += "朝夕心愿已完成,"
        else:
            msg += "朝夕心愿未完成,"
        if self.task_result_list['monthly_pass_task']:
            msg += "奇迹之旅已领取,"
        if self.task_result_list['energy_cost_task']:
            msg += "体力已消耗"
            
        self.update_task_result(message=msg, data=self.task_result_list)


if __name__ == "__main__":
    task = AllInOneTask()
    # result = task.task_run()
    # print(result.to_dict())
    task.step3()
        