from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from whimbox.common.logger import logger
from whimbox.task.background_task import background_manager, BackgroundFeature


# 功能按钮配置列表
FUNCTION_BUTTONS = [
    {
        'label': '一条龙',
        'task_name': 'all_in_one_task',
        'task_params': {},
        'start_message': '开始一条龙，按 / 结束任务\n',
    },
    {
        'label': '自动跑图',
        'task_name': 'load_path',
        'needs_dialog': True,  # 需要弹出对话框
        'dialog_type': 'path_selection',
    },
    {
        'label': '录制路线',
        'task_name': 'record_path',
        'task_params': {},
        'start_message': '开始录制路线，按 / 停止录制\n',
    },
    {
        'label': '自动搓核弹',
        'task_name': 'roll_dice_task',
        'task_params': {},
        'start_message': '开始搓核弹，按 / 手动停止\n随机任务如果满了需要去做，就手动停止，奇想盒默认会继续搓\n',
    }
]


class FunctionView(QWidget):
    """功能菜单视图组件"""
    # 统一的功能按钮点击信号
    function_clicked = pyqtSignal(dict)  # 传递按钮配置字典
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 按钮字典，key为button_id，value为QPushButton对象
        self.buttons = []
        
        # 后台任务相关
        self.background_checkboxes = {}  # 存储后台功能复选框
        self.background_status_label = None  # 后台任务状态标签
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化功能视图UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 后台任务区域
        background_container = self.create_background_task_section()
        layout.addWidget(background_container)
        
        # 功能区域容器
        function_container = QWidget()
        function_container.setStyleSheet("""
            QWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: rgba(240, 240, 240, 150);
            }
        """)
        
        function_layout = QVBoxLayout(function_container)
        function_layout.setContentsMargins(16, 16, 16, 16)
        function_layout.setSpacing(12)
        
        # 根据配置创建所有功能按钮
        for config in FUNCTION_BUTTONS:
            button = self.create_function_button(config)
            self.buttons.append(button)
            function_layout.addWidget(button)
        
        # 添加弹性空间
        function_layout.addStretch()
        
        layout.addWidget(function_container)
    
    def create_function_button(self, config: dict) -> QPushButton:
        """根据配置创建功能按钮"""
        button = QPushButton(config['label'])
        button.setFixedHeight(50)
        button.clicked.connect(lambda: self.on_function_button_clicked(config))
        button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        return button
    
    def on_function_button_clicked(self, config: dict):
        """功能按钮点击统一处理"""
        logger.info(f"Function button clicked: {config['label']}")
        self.function_clicked.emit(config)
    
    def create_background_task_section(self) -> QWidget:
        """创建后台任务区域"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: rgba(240, 240, 240, 150);
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # 标题行
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("自动小功能")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(title)
        
        # 状态标签
        self.background_status_label = QLabel("●")
        self.background_status_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #999;
                border: none;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(self.background_status_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 功能复选框 - 每行两个
        feature_configs = [
            (BackgroundFeature.AUTO_FISHING, "自动钓鱼"),
            (BackgroundFeature.AUTO_DIALOGUE, "自动对话"),
        ]
        
        # 创建网格布局，每行2个
        for i in range(0, len(feature_configs), 2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(12)
            
            # 第一个复选框
            feature1, label1 = feature_configs[i]
            checkbox1 = self._create_checkbox(feature1, label1)
            row_layout.addWidget(checkbox1)
            
            # 第二个复选框（如果存在）
            if i + 1 < len(feature_configs):
                feature2, label2 = feature_configs[i + 1]
                checkbox2 = self._create_checkbox(feature2, label2)
                row_layout.addWidget(checkbox2)
            else:
                row_layout.addStretch()
            
            layout.addLayout(row_layout)
        
        return container
    
    def _create_checkbox(self, feature: BackgroundFeature, label: str) -> QCheckBox:
        """创建复选框"""
        checkbox = QCheckBox(label)
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                color: #000000;
                border: none;
                spacing: 6px;
                background-color: transparent;
            }
        """)
        checkbox.stateChanged.connect(
            lambda state, f=feature: self.on_background_feature_changed(f, state == Qt.Checked)
        )
        self.background_checkboxes[feature] = checkbox
        return checkbox
    
    def on_background_feature_changed(self, feature: BackgroundFeature, enabled: bool):
        """后台功能复选框改变"""
        background_manager.set_feature_enabled(feature, enabled)
        logger.info(f"后台功能 {feature.value} {'启用' if enabled else '禁用'}")
        
        # 检查是否有任何功能被启用
        self._update_background_task_state()
    
    def _update_background_task_state(self):
        """根据复选框状态自动启动或停止后台任务"""
        # 检查是否有任何功能被启用
        any_enabled = any(checkbox.isChecked() for checkbox in self.background_checkboxes.values())
        
        if any_enabled:
            # 有功能被启用，启动后台任务
            if not background_manager.is_running():
                if background_manager.start_background_task():
                    self._update_status_label(True)
                    logger.info("后台任务已自动启动")
        else:
            # 没有功能被启用，停止后台任务
            if background_manager.is_running():
                background_manager.stop_background_task()
                self._update_status_label(False)
                logger.info("后台任务已自动停止")
    
    def _update_status_label(self, running: bool):
        """更新状态标签"""
        if running:
            self.background_status_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    color: #4CAF50;
                    border: none;
                    background-color: transparent;
                }
            """)
        else:
            self.background_status_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    color: #999;
                    border: none;
                    background-color: transparent;
                }
            """)
    
    def set_all_buttons_enabled(self, enabled: bool):
        """设置所有按钮是否可用"""
        for button in self.buttons:
            button.setEnabled(enabled)

