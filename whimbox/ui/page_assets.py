from whimbox.ui.page import UIPage, TitlePage
from whimbox.ui.ui_assets import *
from whimbox.common.keybind import keybind

page_loading = UIPage(check_icon=IconUILoading)

page_main = UIPage(check_icon=IconPageMainFeature)
page_bigmap = UIPage(check_icon=IconUIBigmap)
page_esc = TitlePage("美鸭梨")
page_daily_task = TitlePage("奇想日历")
page_zxxy = UIPage(check_icon=IconZxxyFeature)
page_xhsg = UIPage(check_icon=IconXhsgFeature)
page_dress = UIPage(check_icon=ButtonWardrobeDressDIY)
page_ability = UIPage(check_icon=IconAbilityFeature)
page_huanjing = TitlePage("幻境挑战")
page_huanjing_jihua = TitlePage("素材激化幻境")
page_huanjing_bless = TitlePage("祝福闪光幻境")
page_huanjing_monster = TitlePage("魔物试炼幻境")
page_huanjing_weekly = TitlePage("心之突破幻境")
page_photo = TitlePage("大喵相机")
page_monthly_pass = TitlePage("奇迹之旅")
page_event = TitlePage("活动大厅")

ui_pages = [
    page_main,
    page_bigmap,
    page_daily_task,
    page_zxxy,
    page_xhsg,
    page_esc,
    page_huanjing,
    page_huanjing_jihua,
    page_huanjing_bless,
    page_huanjing_monster,
    page_huanjing_weekly,
    page_photo,
    page_monthly_pass,
    page_event,
    page_dress,
    page_ability,
]

page_main.link(keybind.KEYBIND_MAP, page_bigmap)
page_main.link('esc', page_esc)
page_main.link(keybind.KEYBIND_DAILY_TASK, page_daily_task)
page_main.link(keybind.KEYBIND_DRESS, page_dress)
page_main.link(keybind.KEYBIND_TAKE_PHOTO, page_photo)
page_main.link(keybind.KEYBIND_MONTHLY_PASS, page_monthly_pass)
page_main.link(keybind.KEYBIND_EVENT, page_event)

page_bigmap.link(keybind.KEYBIND_MAP, page_main)

page_esc.link('esc', page_main)

page_daily_task.link('esc', page_main)
page_daily_task.link(ButtonHuanjingGo, page_huanjing)
page_daily_task.link(ButtonZxxyEntrance, page_zxxy)
page_daily_task.link(ButtonXhsgEntrance, page_xhsg)

page_huanjing.link('esc', page_daily_task)
page_huanjing.link(TextHuanjingJihuaEntrace, page_huanjing_jihua)
page_huanjing.link(TextHuanjingBlessEntrace, page_huanjing_bless)
page_huanjing.link(TextHuanjingMonsterEntrace, page_huanjing_monster)
page_huanjing.link(TextHuanjingBossEntrace, page_huanjing_weekly)

page_huanjing_jihua.link('esc', page_huanjing)
page_huanjing_bless.link('esc', page_huanjing)
page_huanjing_monster.link('esc', page_huanjing)
page_huanjing_weekly.link('esc', page_huanjing)

page_zxxy.link("esc", page_daily_task)
page_xhsg.link("esc", page_daily_task)

page_dress.link("esc", page_main)
page_dress.link(TextWardrobeAbilityTab, page_ability)

page_ability.link("esc", page_main)

page_photo.link("esc", page_main)

page_monthly_pass.link("esc", page_main)

page_event.link('esc', page_main)