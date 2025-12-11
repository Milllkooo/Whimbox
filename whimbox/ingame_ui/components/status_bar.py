from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time

class AIStatusBar(QWidget):
    """简化的AI状态栏控件 - 显示在ChatMessageWidget下方"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "thinking"
        self.current_message = ""
        self.start_time = time.time()
        self.animation_timer = QTimer()
        self.animation_frame = 0
        self.init_ui()
        self.setup_animation()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        
        # 状态图标和文字
        self.status_icon = QLabel("🧠")
        self.status_text = QLabel("LLM思考中...")
        self.time_label = QLabel("00:00")
        
        # 设置样式
        self.status_icon.setStyleSheet("font-size: 6pt;")
        self.status_text.setStyleSheet("color: #666; font-size: 6pt;")
        self.time_label.setStyleSheet("color: #999; font-size: 6pt;")
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addStretch()
        
        # 整体样式
        self.setStyleSheet("""
            AIStatusBar {
                background-color: transparent;
                border: none;
                margin: 2px 0px;
            }
        """)
        
        # 更新计时器
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
    
    def setup_animation(self):
        """设置动画"""
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(800)  # 800ms更新一次
    
    def update_animation(self):
        """更新动画效果"""
        if self.current_status == "thinking":
            dots = "." * ((self.animation_frame % 3) + 1)
            self.status_text.setText(f"LLM思考中{dots}")
        elif self.current_status == "on_tool_start":
            dots = "." * ((self.animation_frame % 3) + 1)
            self.status_text.setText(f"工具执行中，请勿操作游戏{dots}")
        elif self.current_status == "generating":
            dots = "." * ((self.animation_frame % 3) + 1)
            self.status_text.setText(f"生成回复中{dots}")
        
        self.animation_frame += 1
    
    def update_time(self):
        """更新用时显示"""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def set_status(self, status_type: str, message: str = ""):
        """更新状态"""
        self.current_status = status_type
        self.current_message = message
        
        status_configs = {
            'thinking': {
                'icon': '🧠',
                'text': 'LLM思考中...',
                'color': '#2196F3'
            },
            'on_tool_start': {
                'icon': '🔧',
                'text': f'工具执行中，请勿操作游戏... {message}',
                'color': '#FF9800'
            },
            'generating': {
                'icon': '📝',
                'text': '生成回复中...',
                'color': '#4CAF50'
            },
            'completed': {
                'icon': '✅',
                'text': '完成',
                'color': '#4CAF50'
            },
            'error': {
                'icon': '❌',
                'text': f'错误: {message}',
                'color': '#F44336'
            }
        }
        
        config = status_configs.get(status_type, status_configs['thinking'])
        self.status_icon.setText(config['icon'])
        
        # 更新边框颜色
        self.setStyleSheet(f"""
            AIStatusBar {{
                background-color: transparent;
                border: none;
                margin: 2px 0px;
            }}
        """)
        
        # 如果是完成状态，停止动画并设置固定文字
        if status_type in ['completed', 'error']:
            self.animation_timer.stop()
            self.status_text.setText(config['text'])
            # 2秒后隐藏
            QTimer.singleShot(2000,  self.deleteLater)

    
    def closeEvent(self, event):
        """关闭时清理定时器"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        super().closeEvent(event)