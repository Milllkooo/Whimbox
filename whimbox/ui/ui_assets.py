from whimbox.ui.template.img_manager import LOG_WHEN_TRUE, LOG_ALL, LOG_NONE, LOG_WHEN_FALSE, ImgIcon
from whimbox.ui.template.button_manager import Button
from whimbox.ui.template.posi_manager import PosiTemplate, Area
from whimbox.ui.template.text_manager import TextTemplate, Text

# 很多界面左上角都有的文字标题区域
AreaPageTitleFeature = Area()

# 主界面、esc菜单、抽卡、商城相关
IconPageMainFeature = ImgIcon(print_log=LOG_NONE, threshold=0.90, gray_limit=(230, 255))
IconDungeonFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.90, gray_limit=(230, 255))
AreaUITime = Area()
AreaEscEntrances = Area()
IconGachaFeature = ImgIcon(print_log=LOG_NONE, threshold=0.99)
IconShopFeature = ImgIcon(print_log=LOG_NONE, threshold=0.99)

# loading界面
IconUILoading = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 大地图相关
IconUIBigmap = ImgIcon(print_log=LOG_WHEN_TRUE)
IconBigMapMaxScale = ImgIcon(print_log=LOG_WHEN_TRUE)
ButtonBigMapZoom = Button(print_log=LOG_WHEN_TRUE)
ButtonBigMapTeleport = ImgIcon(print_log=LOG_WHEN_TRUE)
AreaBigMapRegionName = Area()
AreaBigMapRegionSelect = Area()
AreaBigMapTeleporterSelect = Area()
# 大地图材料追踪
AreaBigMapMaterialTypeSelect = Area()
AreaBigMapMaterialSelect = Area()
AreaBigMapMaterialTrackConfirm = Area()

# 大世界采集、跳跃、移动、跳过等相关的UI
AreaFPickup = Area()
TextFPickUp = Text("拾取", cap_area = AreaFPickup)
IconSkip = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.80, gray_limit=(210, 255)) 
IconClickSkip = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.80, gray_limit=(210, 255))
IconSkipDialog = ImgIcon(print_log=LOG_NONE, threshold=0.75, gray_limit=(210, 255))
AreaMovementWalk = Area()
IconMovementWalking = ImgIcon()
AreaMaterialTrackNear = Area()
AreaMaterialGetText = Area()
AreaAbilityButton = Area()

# 钓鱼相关
IconFishingNoFish = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.90, hsv_limit=([0,0,175], [20,255,255])) # 鱼掉光时候的图标
AreaFishingDetection = Area()  # B区域（鱼进度检测区域）
AreaFishingIcons = Area()
IconFishingHomeFeature = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))      # 取消钓陨星
IconFishingMiralandFeature = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))  # 取消钓鱼
IconFishingFinish = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))  # 收竿图标，容易和收线图标识别错，提高点阈值
IconFishingStrike = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255)) # 提竿图标
IconFishingPullLine = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))  # 大世界拉扯鱼线图标
IconFishingPullLineHome = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))  # 家园拉扯鱼线图标
IconFishingReelIn = ImgIcon(print_log=LOG_NONE, threshold=0.80, gray_limit=(210, 255))  # 收线图标

# 幻境挑战页面
ButtonHuanjingGo = Button(print_log=LOG_WHEN_TRUE)
AreaHuanjingMonsterEntrace = Area()
TextHuanjingMonsterEntrace = Text("魔物试炼幻境", cap_area = AreaHuanjingMonsterEntrace)
AreaHuanjingBlessEntrace = Area()
TextHuanjingBlessEntrace = Text("祝福闪光幻境", cap_area = AreaHuanjingBlessEntrace)
AreaHuanjingZiyangEntrace = Area()
TextHuanjingZiyangEntrace = Text("奇想滋养幻境", cap_area = AreaHuanjingZiyangEntrace)
AreaHuanjingJihuaEntrace = Area()
TextHuanjingJihuaEntrace = Text("素材激化幻境", cap_area = AreaHuanjingJihuaEntrace)
AreaHuanjingBossEntrace = Area()
TextHuanjingBossEntrace = Text("心之突破幻境", cap_area = AreaHuanjingBossEntrace)

# 祝福闪光幻境相关
AreaBlessHuanjingLevelsSelect = Area()
AreaBlessHuanjingDifficulty3 = Area()
TextBlessHuanjingDifficulty3 = Text("困难", cap_area = AreaBlessHuanjingDifficulty3)
ButtonBlessHuanjingQuickPlay = Button(print_log=LOG_WHEN_TRUE)
ButtonBlessHuanjingNumMax = Button(print_log=LOG_WHEN_TRUE)
ButtonBlessHuanjingConfirm = Button(print_log=LOG_WHEN_TRUE)

# 素材激化幻境相关
ButtonJihuaInnerGo = Button(print_log=LOG_WHEN_TRUE)
AreaTextJihuatai = Area()
TextJihuatai = Text("打开素材激化台", cap_area = AreaTextJihuatai)
AreaJihuaTargetSelect = Area()
AreaJihuaCostSelect = Area()
ButtonJihuaNumMax = Button(print_log=LOG_WHEN_TRUE)
ButtonJihuaNumConfirm = Button(print_log=LOG_WHEN_TRUE)
ButtonJihuaFinallyConfirm = Button(print_log=LOG_WHEN_TRUE)

# 魔物试炼幻境相关
# 基本可以复用祝福闪光幻境

# 美鸭梨挖掘相关
ButtonDigGather = Button(print_log=LOG_WHEN_TRUE)
ButtonDigGatherConfirm = Button(print_log=LOG_WHEN_TRUE)
ButtonDigAgain = Button(print_log=LOG_WHEN_TRUE)
AreaDigingNumText = Area()
AreaDigMainTypeSelect = Area()
AreaDigSubTypeSelect = Area()
AreaDigItemSelect = Area()
ButtonDigConfirm = Button(print_log=LOG_WHEN_TRUE)
ButtonDigTime20h = Button(print_log=LOG_WHEN_TRUE)

# 朝夕心愿相关
ButtonZxxyEntrance = Button(print_log=LOG_WHEN_TRUE)
IconZxxyFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.90, hsv_limit=([20, 15, 250], [30, 190, 255]))
AreaZxxyScore = Area()
ButtonZxxyRewarded = Button(print_log=LOG_WHEN_TRUE)
ButtonZxxyTask1 = Button()
ButtonZxxyTask2 = Button()
ButtonZxxyTask3 = Button()
ButtonZxxyTask4 = Button()
ButtonZxxyTask5 = Button()
AreaZxxyTaskText = Area()
IconUIZxxyTaskFinished = ImgIcon(print_log=LOG_WHEN_TRUE)

# 星海拾遗相关
ButtonXhsyEntrance = Button(print_log=LOG_WHEN_TRUE)
IconUIXhsy = ImgIcon(print_log=LOG_WHEN_TRUE)

# 换装界面
AreaWardrobeTab1 = Area()
TextWardrobeDressTab = Text("换装", cap_area = AreaWardrobeTab1)
ButtonWardrobeDressDIY = Button(print_log=LOG_WHEN_TRUE)

# 能力配置界面
AreaWardrobeTab3 = Area()
TextWardrobeAbilityTab = Text("能力配置", cap_area = AreaWardrobeTab3)
AreaWardrobeAbilityBattleText = Area()
TextWardrobeAbilityBattle = Text("净化", cap_area = AreaWardrobeAbilityBattleText)
IconAbilityFloat = ImgIcon()    # 泡泡套跳跃
IconAbilityWing = ImgIcon()    # 飞鸟套跳跃
IconAbilityAnimal = ImgIcon()    # 清洁
IconAbilityInsect = ImgIcon()      # 捕虫
IconAbilityFish = ImgIcon()     # 钓鱼
IconAbilityFly = ImgIcon()      # 滑翔
IconAbilitySmall = ImgIcon()    # 变小
AreaAbilityChange = Area()
ButtonAbilitySave = Button(print_log=LOG_WHEN_TRUE)
AreaAbilityPlanChangeButton = Area()
AreaAbilityPlan1Button = Area()
AreaAbilityPlan2Button = Area()
AreaAbilityPlan3Button = Area()

# 素材相关
IconMaterialTypeAnimal = ImgIcon()
IconMaterialTypePlant = ImgIcon()
IconMaterialTypeInsect = ImgIcon()
IconMaterialTypeFish = ImgIcon()
IconMaterialTypeMonster = ImgIcon()
IconMaterialTypeOther = ImgIcon()
IconMaterialTypeDig1 = ImgIcon()

# 拍照相关
IconPhotoEdit = ImgIcon(print_log=LOG_WHEN_TRUE)
IconPhotoDelete = ImgIcon()
ButtonPhotoDeleteConfirm = Button(print_log=LOG_WHEN_TRUE)

# 大月卡，奇迹之旅
ButtonMonthlyPassAward = Button(print_log=LOG_WHEN_TRUE)
ButtonMonthlyPassTab1 = Button(print_log=LOG_WHEN_TRUE)
ButtonMonthlyPassTab2 = Button(print_log=LOG_WHEN_TRUE)

# 奇迹之冠
AreaMiraCrownOverview = Area()
ButtonMiraCrownQuickPlay = Button(print_log=LOG_WHEN_TRUE)

# 活动相关
# 1.11大富翁活动
ButtonMonopolyEntrance = Button(print_log=LOG_WHEN_TRUE)
ButtonMonopolyConfirmDailyAward = Button(print_log=LOG_WHEN_TRUE)
ButtonMonopolySendBullet = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonopolyCloseBullet = Button(print_log=LOG_WHEN_TRUE)
AreaMonopolyDiceNum = Area()
IconMonopolyMapFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconMonopolyMapFeature2 = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconMonopolyNikkiFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonopolyRollDice = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonopolyStopFunBox = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaMonopolyFunboxOptions = Area()
ButtonMonopolyStartQuestion = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
# IconMonopolyQuestionFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaMonopolyQuestion = Area()
AreaMonopolyAnswer = Area()
ButtonMonopolyLeaveGrid = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonopolyConfirmEvent = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconMonopolyTicketFeature = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonopolyTaskFull = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
