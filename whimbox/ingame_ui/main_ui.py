import win32gui
import win32con
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput import keyboard
import sys
from importlib.metadata import version, PackageNotFoundError

from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.common.logger import logger
from whimbox.config.config import global_config

from whimbox.ingame_ui.components import SettingsDialog, ChatView, PathSelectionDialog, MacroSelectionDialog, FunctionView
from whimbox.ingame_ui.workers.call_worker import TaskCallWorker
from whimbox.task.background_task.background_task import background_manager

update_time = 500  # ui更新间隔，ms

class IngameUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # 状态管理
        self.is_expanded = False
        self.focus_on_game = True
        self.current_view = 'chat'  # 'function' 或 'chat'
        self.waiting_for_task_stop = False  # 等待任务停止标志
        self.is_minimized = False  # 窗口最小化状态
        
        # UI组件
        self.expanded_widget = None
        self.chat_view = None  # ChatView组件
        self.function_view = None  # FunctionView组件
        self.view_toggle_button = None  # 视图切换按钮
        self.settings_dialog = None
        self.path_dialog = None
        self.macro_dialog = None
        self.task_worker = None  # 任务worker
        self.title_label = None  # 标题标签（用于焦点状态显示）
        
        # 拖动相关变量
        self.dragging = False
        self.drag_position = QPoint()
        # 从配置文件加载UI窗口的屏幕位置
        pos_x = global_config.get_int("General", "ui_position_x", 10)
        pos_y = global_config.get_int("General", "ui_position_y", 10)
        self.saved_position = QPoint(pos_x, pos_y)
        
        # 窗口大小调整相关变量
        self.resizing = False
        self.resize_edge = None  # 'left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()
        self.resize_margin = 10  # 边缘检测范围（像素）
        
        # 从配置文件加载窗口大小
        saved_width = global_config.get_int("General", "ui_width", 500)
        saved_height = global_config.get_int("General", "ui_height", 600)
        self.saved_size = QSize(saved_width, saved_height)
        
        # 初始化UI
        self.init_ui()
        
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui_position)
        self.timer.start(update_time)

        # 窗口设置
        self.setWindowTitle("奇想盒")
        # # 获取打包后的图标路径
        # icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        # if icon_path.exists():
        #     self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
        self.position_window()
        self.acquire_focus()
        
        # 键盘监听
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.daemon = True
        self.listener.start()

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('/'):
            QTimer.singleShot(0, self.on_slash_pressed)
        elif key == keyboard.Key.esc:
            QTimer.singleShot(0, self.on_esc_pressed)
    
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建展开状态组件
        self.create_expanded_widget()
        
        # 默认显示展开状态
        self.show_expanded()
        
        # 添加欢迎消息（仅在首次展开时）
        if self.chat_view and not self.chat_view.has_messages():
            self.chat_view.add_message("👋 您好！我是奇想盒📦，你可以直接选择功能，或者和我聊天。", 'ai')
            self.chat_view.add_message("❗请确认游戏分辨率为1920x1080或2560x1440。如已设置，请忽略~", "ai")
    
    def create_expanded_widget(self):
        """创建展开状态的聊天界面"""
        self.expanded_widget = QWidget(self)
        # 使用最小尺寸替代固定尺寸，允许调整大小
        self.expanded_widget.setMinimumSize(300, 350)
        self.expanded_widget.resize(self.saved_size)
        self.expanded_widget.setObjectName("expandedWidget")
        # 初始样式（无焦点状态）
        self.expanded_widget.setStyleSheet("""
            QWidget#expandedWidget {
                background-color: rgba(255, 255, 255, 120);
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # 为expanded_widget安装事件过滤器以处理鼠标事件
        self.expanded_widget.installEventFilter(self)
        self.expanded_widget.setMouseTracking(True)
        
        # 主布局
        layout = QVBoxLayout(self.expanded_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 创建拖动横条容器（用于居中）
        drag_bar_container = QHBoxLayout()
        drag_bar_container.setContentsMargins(0, 0, 0, 0)
        drag_bar_container.addStretch()
        
        # 创建拖动横条
        drag_bar = QLabel()
        drag_bar.setFixedSize(200, 8)
        drag_bar.setCursor(Qt.SizeAllCursor)
        drag_bar.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #BDBDBD;
            }
            QLabel:hover {
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
            }
        """)
        drag_bar.mousePressEvent = self.drag_bar_mouse_press
        drag_bar.mouseMoveEvent = self.drag_bar_mouse_move
        drag_bar.mouseReleaseEvent = self.drag_bar_mouse_release
        
        drag_bar_container.addWidget(drag_bar)
        drag_bar_container.addStretch()
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignVCenter)  # 垂直居中对齐
        self.title_label = QLabel("⚪ 📦 奇想盒 [按 / 激活窗口]")
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 16px;
                font-weight: bold; 
                border: none; 
            }
        """)
        
        # 版本号标签
        try:
            app_version = version("whimbox")
        except PackageNotFoundError:
            app_version = "dev"
        
        version_label = QLabel(app_version)
        version_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1976D2;
                font-size: 12px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 8px;
                border: 1px solid #2196F3;
                margin-top: 3px;
            }
        """)
        version_label.setFixedHeight(20)
        
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(25, 25)
        settings_button.clicked.connect(self.open_settings)
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        minimize_button = QPushButton("➖")
        minimize_button.setFixedSize(25, 25)
        minimize_button.clicked.connect(self.toggle_minimize)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFF9C4;
                border: 2px solid #FBC02D;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #F9A825;
            }
        """)

        close_button = QPushButton("❌")
        close_button.setFixedSize(25, 25)
        close_button.clicked.connect(self.close_application)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        title_layout.addWidget(settings_button)
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(close_button)
        
        # 视图切换按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 4, 0, 4)
        
        self.view_toggle_button = QPushButton("🎯 功能菜单")
        self.view_toggle_button.setFixedHeight(40)
        self.view_toggle_button.clicked.connect(self.toggle_view)
        self.view_toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        button_layout.addWidget(self.view_toggle_button)
        
        # 创建功能视图组件
        self.function_view = FunctionView(self.expanded_widget)
        self.function_view.function_clicked.connect(self.on_function_clicked)
        
        # 创建聊天视图组件
        self.chat_view = ChatView(self.expanded_widget)
        # 连接焦点管理信号
        self.chat_view.request_focus.connect(self.on_agent_task_request_focus)
        self.chat_view.release_focus.connect(self.on_agent_task_release_focus)
        
        # 组装布局
        layout.addLayout(drag_bar_container)
        layout.addLayout(title_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.function_view, 1)
        layout.addWidget(self.chat_view, 1)
        
        # 默认显示聊天视图
        self.function_view.hide()
    
    def toggle_view(self):
        """切换视图（功能菜单 <-> 对话框）"""
        if self.current_view == 'function':
            # 切换到聊天视图
            self.current_view = 'chat'
            self.function_view.hide()
            self.chat_view.show()
            self.view_toggle_button.setText("🎯 功能菜单")
            logger.info("Switched to chat view")
        else:
            # 切换到功能视图
            self.current_view = 'function'
            self.chat_view.hide()
            self.function_view.show()
            self.view_toggle_button.setText("💬 返回对话框")
            logger.info("Switched to function view")
    
    def switch_to_chat_view(self):
        """切换到聊天视图"""
        if self.current_view != 'chat':
            self.current_view = 'chat'
            self.function_view.hide()
            self.chat_view.show()
            self.view_toggle_button.setText("🎯 功能菜单")
            logger.info("Switched to chat view")
    
    def on_function_clicked(self, config: dict):
        """统一处理功能按钮点击"""
        self.give_back_focus()
        # shape_ok, width, height = HANDLE_OBJ.check_shape()
        # logger.info(f"分辨率: {width}x{height}")
        # if not shape_ok:
        #     self.chat_view.add_message("请先将游戏的显示模式设置为窗口模式，分辨率设置为1920x1080或2560x1440", 'error')
        #     self.switch_to_chat_view()
        #     return
        
        # 检查是否已有任务在运行
        if self.task_worker and self.task_worker.isRunning():
            self.chat_view.add_message("已有任务正在运行中，请稍候...", "ai")
            self.switch_to_chat_view()
            return
        
        # 切换到聊天视图
        self.switch_to_chat_view()
        
        # 如果需要弹出对话框
        if config.get('needs_dialog'):
            if config['dialog_type'] == 'path_selection':
                self.path_dialog = PathSelectionDialog(self)
                self.path_dialog.path_selected.connect(lambda path: self.start_task_with_path(config, path))
                self.path_dialog.show_centered()
                self.path_dialog.exec_()
            elif config['dialog_type'] == 'macro_selection':
                self.macro_dialog = MacroSelectionDialog(self)
                self.macro_dialog.macro_selected.connect(lambda macro: self.start_task_with_macro(config, macro))
                self.macro_dialog.show_centered()
                self.macro_dialog.exec_()
        else:
            # 直接启动任务
            self.start_task(config)
    
    def start_task(self, config: dict):
        """启动任务"""
        # 将焦点返回给游戏
        self.give_back_focus(title_text="⚪ 📦 奇想盒 [任务运行中，按 / 结束任务]")
        
        # 禁用所有按钮
        if self.function_view:
            self.function_view.set_all_buttons_enabled(False)
        
        # 在聊天视图中显示消息
        if self.chat_view and config.get('start_message'):
            self.chat_view.add_message(config['start_message'], 'ai')
        
        # 创建并启动worker
        self.task_worker = TaskCallWorker(config['task_name'], config.get('task_params', {}))
        self.task_worker.progress.connect(self.on_task_progress)
        self.task_worker.finished.connect(self.on_task_finished)
        self.task_worker.start()
        
        logger.info(f"Task started: {config['task_name']}")
    
    def start_task_with_path(self, config: dict, path_name: str):
        """启动需要路径参数的任务"""
        # 将焦点返回给游戏
        self.give_back_focus(title_text="⚪ 📦 奇想盒 [任务运行中，按 / 结束任务]")
        
        # 禁用所有按钮
        if self.function_view:
            self.function_view.set_all_buttons_enabled(False)
        
        # 在聊天视图中显示消息
        if self.chat_view:
            self.chat_view.add_message(f'开始自动跑图：{path_name}，按 / 结束任务\n', 'ai')
        
        # 合并路径参数
        params = dict(config.get('task_params', {}))
        params['path_name'] = path_name
        
        # 创建并启动worker
        self.task_worker = TaskCallWorker(config['task_name'], params)
        self.task_worker.progress.connect(self.on_task_progress)
        self.task_worker.finished.connect(self.on_task_finished)
        self.task_worker.start()
        
        logger.info(f"Task started: {config['task_name']} with path: {path_name}")
    
    def start_task_with_macro(self, config: dict, macro_name: str):
        """启动需要宏参数的任务"""
        # 将焦点返回给游戏
        self.give_back_focus(title_text="⚪ 📦 奇想盒 [任务运行中，按 / 结束任务]")
        
        # 禁用所有按钮
        if self.function_view:
            self.function_view.set_all_buttons_enabled(False)
        
        # 在聊天视图中显示消息
        if self.chat_view:
            self.chat_view.add_message(f'开始运行宏：{macro_name}，按 / 结束任务\n', 'ai')
        
        # 合并宏参数
        params = dict(config.get('task_params', {}))
        params['macro_name'] = macro_name
        
        # 创建并启动worker
        self.task_worker = TaskCallWorker(config['task_name'], params)
        self.task_worker.progress.connect(self.on_task_progress)
        self.task_worker.finished.connect(self.on_task_finished)
        self.task_worker.start()
        
        logger.info(f"Task started: {config['task_name']} with macro: {macro_name}")
    
    def on_task_progress(self, message: str):
        """处理任务进度消息"""
        logger.info(f"Task progress: {message}")
        if self.chat_view:
            self.chat_view.add_message(message, 'ai')
    
    def on_task_finished(self, success: bool, result):
        """处理任务完成"""
        # 恢复所有按钮状态
        if self.function_view:
            self.function_view.set_all_buttons_enabled(True)
        
        if success:
            if self.chat_view:
                self.chat_view.add_message(f"✅ 任务完成: {result['message']}", 'ai')
        else:
            if self.chat_view:
                self.chat_view.add_message(f"❌ 任务失败：{result['message']}", 'error')
        
        # 清理worker
        if self.task_worker:
            self.task_worker.deleteLater()
            self.task_worker = None
        
        # 如果是等待任务停止状态，现在可以切换焦点了
        if self.waiting_for_task_stop:
            self.waiting_for_task_stop = False
            self.expand_chat()
        else:
            # 正常完成，只获取焦点
            self.acquire_focus()
    
    def on_agent_task_release_focus(self, title_text: str):
        """Agent任务开始时释放焦点"""
        self.give_back_focus(title_text)
    
    def on_agent_task_request_focus(self):
        """Agent任务完成时请求焦点"""
        # 如果是等待任务停止状态，说明用户按了 /，现在任务结束了
        if self.waiting_for_task_stop:
            self.waiting_for_task_stop = False
            self.expand_chat()
        else:
            # 正常完成，只获取焦点（不展开，因为用户可能在聊天界面）
            self.acquire_focus()
    
    def show_expanded(self):
        """显示展开状态"""
        self.is_expanded = True
        if self.expanded_widget:
            self.expanded_widget.show()
        # 根据expanded_widget的大小设置主窗口大小，留出边距
        widget_size = self.expanded_widget.size()
        self.setGeometry(0, 0, widget_size.width() + 20, widget_size.height() + 20)

    def expand_chat(self):
        """展开聊天界面"""
        logger.info("Expanding chat interface")
        self.show_expanded()
        self.position_window()
        self.acquire_focus()
        
        # 延迟设置焦点，确保窗口完全展开
        QTimer.singleShot(100, lambda: self.chat_view.set_focus_to_input() if self.chat_view else None)
    
    def toggle_minimize(self):
        """切换窗口最小化状态"""
        if self.is_minimized or self.windowState() & Qt.WindowMinimized:
            # 窗口已最小化，恢复窗口
            self.setWindowState(Qt.WindowActive)
            self.showNormal()
            self.is_minimized = False
            logger.info("Window restored from taskbar")
        else:
            # 窗口未最小化，最小化窗口
            self.showMinimized()
            self.is_minimized = True
            logger.info("Window minimized to taskbar")
    
    def close_application(self):
        """关闭应用程序"""
        # 创建确认对话框
        reply = QMessageBox.question(
            self,
            '确认关闭',
            '确定要关闭奇想盒吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("User confirmed - closing whimbox")
            sys.exit(0)
    
    def open_settings(self):
        """打开设置对话框"""
        logger.info("Opening settings dialog")
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show_centered()
        self.settings_dialog.exec_()
    
    def update_focus_visual(self, has_focus: bool, title_text: str = "⚪ 📦 奇想盒 [按 / 激活窗口]"):
        """更新焦点视觉状态"""
        if not self.expanded_widget or not self.title_label:
            return
        
        if has_focus:
            # 有焦点：蓝色粗边框 + 发光效果
            self.expanded_widget.setStyleSheet("""
                QWidget#expandedWidget {
                    background-color: rgba(255, 255, 255, 120);
                    border-radius: 12px;
                    border: 3px solid #2196F3;
                }
            """)
            self.title_label.setText("🟢 📦 奇想盒")
        else:
            # 无焦点：灰色细边框
            self.expanded_widget.setStyleSheet("""
                QWidget#expandedWidget {
                    background-color: rgba(255, 255, 255, 120);
                    border-radius: 12px;
                    border: 1px solid #E0E0E0;
                }
            """)
            self.title_label.setText(title_text)

    def acquire_focus(self):
        # 移除透明窗口设置，使窗口可以接收输入
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_TRANSPARENT)
        # 激活窗口并获取焦点
        self.setWindowState(Qt.WindowMinimized)
        self.setWindowState(Qt.WindowActive)
        self.focus_on_game = False
        # 更新视觉状态
        self.update_focus_visual(True)

    def give_back_focus(self, title_text: str = "⚪ 📦 奇想盒 [按 / 激活窗口]"):
        # 恢复透明窗口设置
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
        # 将焦点返回给游戏
        HANDLE_OBJ.set_foreground()
        self.focus_on_game = True
        # 更新视觉状态
        self.update_focus_visual(False, title_text)

    def position_window(self):
        self.move(self.saved_position)

    def on_slash_pressed(self):
        """处理斜杠键按下事件"""
        if win32gui.GetForegroundWindow() != HANDLE_OBJ.get_handle():
            return
        
        # 如果已经在等待任务停止，忽略重复按键
        if self.waiting_for_task_stop:
            return
        
        # 检查是否有手动任务或Agent任务正在运行
        has_manual_task = self.task_worker and self.task_worker.isRunning()
        has_agent_task = self.chat_view and self.chat_view.current_worker and self.chat_view.current_worker.isRunning()
        
        if has_manual_task or has_agent_task:
            # 任务正在运行，只更新标题，不切换焦点
            # 任务会自己检测到 / 键并停止（在 task_template.py 中）
            self.waiting_for_task_stop = True
            self.update_focus_visual(False, "⚪ 📦 奇想盒 [等待任务结束中…]")
            logger.info("Waiting for task to stop...")
        else:
            # 没有任务运行，正常展开聊天窗口
            self.expand_chat()
    
    def on_esc_pressed(self):
        """处理ESC键按下事件"""
        if win32gui.GetForegroundWindow() != int(self.winId()):
            return
        self.toggle_minimize()
    
    def update_ui_position(self):
        """定时更新，处理窗口隐藏"""
        if self.isVisible():
            if HANDLE_OBJ.is_foreground() and not self.focus_on_game:
                self.give_back_focus()
            elif not HANDLE_OBJ.is_foreground() and self.focus_on_game:
                self.acquire_focus()
    
    def update_message(self, message: str, type="update_ai_message"):
        """更新聊天消息"""
        if self.chat_view:
            self.chat_view.ui_update_signal.emit(type, message)
    
    def drag_bar_mouse_press(self, event):
        """拖动横条按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def drag_bar_mouse_move(self, event):
        """拖动横条移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 计算新位置（基于屏幕坐标）
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            # 更新保存的位置
            self.saved_position = new_pos
            event.accept()
    
    def drag_bar_mouse_release(self, event):
        """拖动横条释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # 保存位置到配置文件
            if self.saved_position:
                global_config.set("General", "ui_position_x", self.saved_position.x())
                global_config.set("General", "ui_position_y", self.saved_position.y())
                global_config.save()
                logger.info(f"UI position saved: ({self.saved_position.x()}, {self.saved_position.y()})")
            event.accept()
    
    def get_resize_edge(self, pos: QPoint) -> str:
        """检测鼠标位置是否在窗口边缘，返回边缘类型"""
        rect = self.expanded_widget.rect()
        margin = self.resize_margin
        
        # 检测角落（优先级高）
        if pos.x() <= margin and pos.y() <= margin:
            return 'topleft'
        elif pos.x() >= rect.width() - margin and pos.y() <= margin:
            return 'topright'
        elif pos.x() <= margin and pos.y() >= rect.height() - margin:
            return 'bottomleft'
        elif pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
            return 'bottomright'
        # 检测边
        elif pos.x() <= margin:
            return 'left'
        elif pos.x() >= rect.width() - margin:
            return 'right'
        elif pos.y() <= margin:
            return 'top'
        elif pos.y() >= rect.height() - margin:
            return 'bottom'
        return None
    
    def get_cursor_for_edge(self, edge: str) -> Qt.CursorShape:
        """根据边缘类型返回对应的鼠标指针样式"""
        cursor_map = {
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'topleft': Qt.SizeFDiagCursor,
            'bottomright': Qt.SizeFDiagCursor,
            'topright': Qt.SizeBDiagCursor,
            'bottomleft': Qt.SizeBDiagCursor,
        }
        return cursor_map.get(edge, Qt.ArrowCursor)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理窗口大小调整"""
        if obj == self.expanded_widget:
            if event.type() == QEvent.MouseMove:
                if self.resizing:
                    # 正在调整大小
                    self.handle_resize(event.globalPos())
                    return True
                else:
                    # 更新鼠标指针
                    edge = self.get_resize_edge(event.pos())
                    if edge:
                        self.expanded_widget.setCursor(self.get_cursor_for_edge(edge))
                    else:
                        self.expanded_widget.setCursor(Qt.ArrowCursor)
            
            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    edge = self.get_resize_edge(event.pos())
                    if edge:
                        # 开始调整大小
                        self.resizing = True
                        self.resize_edge = edge
                        self.resize_start_pos = event.globalPos()
                        self.resize_start_geometry = self.expanded_widget.geometry()
                        return True
            
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton and self.resizing:
                    # 结束调整大小
                    self.resizing = False
                    self.resize_edge = None
                    # 保存大小到配置
                    self.saved_size = self.expanded_widget.size()
                    global_config.set("General", "ui_width", self.saved_size.width())
                    global_config.set("General", "ui_height", self.saved_size.height())
                    global_config.save()
                    logger.info(f"UI size saved: ({self.saved_size.width()}, {self.saved_size.height()})")
                    return True
        
        return super().eventFilter(obj, event)
    
    def handle_resize(self, global_pos: QPoint):
        """处理窗口大小调整"""
        delta = global_pos - self.resize_start_pos
        new_geometry = QRect(self.resize_start_geometry)
        min_width = self.expanded_widget.minimumWidth()
        min_height = self.expanded_widget.minimumHeight()
        
        # 标记是否达到最小尺寸
        width_clamped = False
        height_clamped = False
        
        # 根据边缘类型调整窗口大小和位置
        if 'left' in self.resize_edge:
            new_width = self.resize_start_geometry.width() - delta.x()
            if new_width >= min_width:
                new_geometry.setLeft(self.resize_start_geometry.left() + delta.x())
                new_geometry.setWidth(new_width)
            else:
                # 达到最小宽度，锁定在最小值
                new_geometry.setWidth(min_width)
                new_geometry.setLeft(self.resize_start_geometry.right() - min_width)
                width_clamped = True
        
        if 'right' in self.resize_edge:
            new_width = self.resize_start_geometry.width() + delta.x()
            if new_width >= min_width:
                new_geometry.setWidth(new_width)
            else:
                # 达到最小宽度，锁定在最小值
                new_geometry.setWidth(min_width)
                width_clamped = True
        
        if 'top' in self.resize_edge:
            new_height = self.resize_start_geometry.height() - delta.y()
            if new_height >= min_height:
                new_geometry.setTop(self.resize_start_geometry.top() + delta.y())
                new_geometry.setHeight(new_height)
            else:
                # 达到最小高度，锁定在最小值
                new_geometry.setHeight(min_height)
                new_geometry.setTop(self.resize_start_geometry.bottom() - min_height)
                height_clamped = True
        
        if 'bottom' in self.resize_edge:
            new_height = self.resize_start_geometry.height() + delta.y()
            if new_height >= min_height:
                new_geometry.setHeight(new_height)
            else:
                # 达到最小高度，锁定在最小值
                new_geometry.setHeight(min_height)
                height_clamped = True
        
        # 应用新的几何属性
        self.expanded_widget.setGeometry(new_geometry)
        
        # 如果达到了最小尺寸，更新起始参考点，避免反弹
        if width_clamped or height_clamped:
            self.resize_start_geometry = self.expanded_widget.geometry()
            self.resize_start_pos = global_pos
        
        # 同步更新主窗口的大小
        widget_size = self.expanded_widget.size()
        self.setGeometry(self.geometry().x(), self.geometry().y(), 
                        widget_size.width() + 20, widget_size.height() + 20)
    
    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                # 窗口被最小化
                self.is_minimized = True
                logger.info("Window minimized")
            else:
                # 窗口被恢复
                if self.is_minimized:
                    self.is_minimized = False
                    logger.info("Window restored")
        super().changeEvent(event)


    # def log_poster(self, log_str: str):
    #     """处理格式化日志输出"""
    #     if DEMO_MODE:
    #         if "DEMO" not in log_str:
    #             return
        
    #     # 简化处理，直接添加到聊天
    #     if "\x1b[" in log_str:
    #         import re
    #         clean_text = re.sub(r'\x1b\[[0-9;]*m', '', log_str)
    #     else:
    #         clean_text = log_str
        
    #     if clean_text.strip():
    #         # 通过信号触发UI更新，确保在主线程中执行
    #         self.ui_update_signal.emit("add_log_message", clean_text.strip())