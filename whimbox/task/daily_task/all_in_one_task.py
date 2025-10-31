'''朝夕心愿一条龙'''

from whimbox.task.task_template import STATE_TYPE_SUCCESS, TaskTemplate, register_step
from whimbox.task import daily_task
from whimbox.task.navigation_task.auto_path_task import AutoPathTask
from whimbox.task.photo_task.daily_photo_task import DailyPhotoTask
from whimbox.config.config import global_config
from whimbox.task.daily_task.cvar import *


class AllInOneTask(TaskTemplate):
    def __init__(self):
        super().__init__("all_in_one_task")
        self.zhaoxi_todo_list = []
        self.task_result_list = {
            'dig_task': False,
            'zhaoxi_task': False,
            'monthly_pass_task': False,
            'energy_cost_task': False,
        }

    @register_step("美鸭梨挖掘")
    def step1(self):
        dig_task = daily_task.DigTask()
        task_result = dig_task.task_run()
        self.task_result_list['dig_task'] = task_result.data

    @register_step("检查朝夕心愿进度")
    def step2(self):
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        self.zhaoxi_todo_list = task_result.data
        if task_result.status == STATE_TYPE_SUCCESS:
            if len(self.zhaoxi_todo_list) == 0:
                self.task_result_list['zhaoxi_task'] = True
                return "step4"
            self.log_to_gui(task_result.message)
        else:
            self.log_to_gui(task_result.message, is_error=True)
            return "step4"

    @register_step("开始完成朝夕心愿任务")
    def step3(self):
        task_dict = {
            DAILY_TASK_PICKUP: AutoPathTask(path_name="朝夕心愿_采集", excepted_num=5),
            DAILY_TASK_CATCH_INSECT: AutoPathTask(path_name="朝夕心愿_捕虫", excepted_num=3),
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
    def step4(self):
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
        if len(self.zhaoxi_todo_list) == 0:
            return "step6"
        else:
            return "step5"
    
    @register_step("获取朝夕心愿奖励")
    def step5(self):
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        self.zhaoxi_todo_list = task_result.data
        if len(self.zhaoxi_todo_list) == 0:
            self.task_result_list['zhaoxi_task'] = True
        else:
            self.task_result_list['zhaoxi_task'] = False

    @register_step("领取奇迹之旅奖励")
    def step6(self):
        monthly_pass_task = daily_task.MonthlyPassTask()
        monthly_pass_task.task_run()
        self.task_result_list['monthly_pass_task'] = True

    @register_step("一条龙结束")
    def step7(self):
        msg = ""
        if self.task_result_list['dig_task']:
            msg += "美鸭梨挖掘成功,"
        else:
            msg += "美鸭梨挖掘还无法收获,"
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
    result = task.task_run()
    print(result.to_dict())
        