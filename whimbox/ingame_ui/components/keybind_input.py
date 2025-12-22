"""键位绑定输入组件"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput import keyboard, mouse

from whimbox.common.logger import logger


class CaptureSignals(QObject):
    """用于发送捕获信号的辅助类"""
    key_captured = pyqtSignal(str)
    capture_cancelled = pyqtSignal()


class KeybindInput(QWidget):
    """键位绑定输入控件"""
    value_changed = pyqtSignal(str)  # 值改变信号
    
    def __init__(self, label_text: str, initial_value: str = "", parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.current_value = initial_value
        self.previous_value = initial_value  # 保存之前的值，用于ESC恢复
        self.input_field = None
        self.is_capturing = False  # 是否正在捕获按键
        self.keyboard_listener = None
        self.mouse_listener = None
        
        # 创建信号对象
        self.capture_signals = CaptureSignals()
        self.capture_signals.key_captured.connect(self.accept_capture)
        self.capture_signals.capture_cancelled.connect(self.cancel_capture)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标签
        label = QLabel(self.label_text)
        label.setWordWrap(False)
        label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 8pt;
            }
        """)
        layout.addWidget(label)
        layout.addStretch()
        
        # 使用 QLabel 作为可点击的按键显示区域
        self.input_field = QLabel()
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setCursor(Qt.PointingHandCursor)
        self.input_field.setFixedHeight(35)
        self.input_field.setFixedWidth(120)
        self.update_display()
        self.update_input_style(False)
        
        # 点击事件
        self.input_field.mousePressEvent = self.on_input_clicked
        
        layout.addWidget(self.input_field)
    
    def update_display(self):
        """更新显示内容"""
        if self.is_capturing:
            # 捕获状态显示提示
            self.input_field.setText("请按下按键")
        elif self.current_value:
            # 直接显示原始按键名
            self.input_field.setText(self.current_value)
        else:
            # 空值显示提示
            self.input_field.setText("点击设置按键")
    
    def update_input_style(self, capturing: bool):
        """更新输入框样式"""
        if capturing:
            # 捕获状态：高亮显示，动画效果
            self.input_field.setStyleSheet("""
                QLabel {
                    padding: 4px;
                    border: 2px solid #2196F3;
                    border-radius: 6px;
                    font-size: 8pt;
                    background-color: #E3F2FD;
                    color: #2196F3;
                    font-weight: bold;
                }
            """)
        else:
            # 正常状态：显示按键值
            self.input_field.setStyleSheet("""
                QLabel {
                    padding: 4px;
                    border: 1px solid #BDBDBD;
                    border-radius: 6px;
                    font-size: 8pt;
                    background-color: white;
                    color: #424242;
                    font-weight: bold;
                }
                QLabel:hover {
                    border: 2px solid #2196F3;
                    background-color: #E3F2FD;
                    color: #2196F3;
                }
            """)
    
    def on_input_clicked(self, event):
        """输入框点击事件"""
        # 只响应鼠标左键点击
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        
        event.accept()
        
        # 如果已经在捕获状态，忽略
        if self.is_capturing:
            return
        
        # 开始捕获
        self.start_capture()
    
    def start_capture(self):
        """开始捕获按键"""
        self.is_capturing = True
        self.previous_value = self.current_value  # 保存当前值
        
        # 更新显示和样式
        self.update_display()
        self.update_input_style(True)
        
        try:
            # 启动键盘监听器
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_keyboard_press,
                suppress=False
            )
            self.keyboard_listener.start()
            
            # 启动鼠标监听器
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click,
                suppress=False
            )
            self.mouse_listener.start()
            
            logger.info("开始捕获按键...")
            
        except Exception as e:
            logger.error(f"启动按键捕获失败: {e}")
            self.cancel_capture()
    
    def on_keyboard_press(self, key):
        """键盘按键事件处理"""
        try:
            # 获取按键名称
            if hasattr(key, 'char') and key.char is not None:
                # 字符键
                key_name = key.char
            else:
                # 特殊键
                key_name = str(key).replace('Key.', '')
            
            # 特殊处理：ESC键取消
            if key_name.lower() == 'esc':
                self.capture_signals.capture_cancelled.emit()
                return False
            
            # 记录捕获的按键
            self.capture_signals.key_captured.emit(key_name)
            
            # 返回False停止监听
            return False
            
        except Exception as e:
            logger.error(f"处理键盘事件失败: {e}")
            return True
    
    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        try:
            # 只处理按下事件
            if not pressed:
                return True
            
            # 检查点击位置是否在输入框范围内（忽略激活点击）
            input_geometry = self.input_field.geometry()
            input_global_pos = self.input_field.mapToGlobal(input_geometry.topLeft())
            input_x = input_global_pos.x()
            input_y = input_global_pos.y()
            input_width = input_geometry.width()
            input_height = input_geometry.height()
            
            # 如果点击在输入框内部，忽略（这是激活点击）
            if (input_x <= x <= input_x + input_width and 
                input_y <= y <= input_y + input_height):
                return True
            
            # 获取鼠标按键名称
            button_name = str(button).replace('Button.', '')
            key_name = f"mouse_{button_name}"
            
            # 如果是鼠标左键，退出编辑模式（取消）
            if key_name == "mouse_left":
                self.capture_signals.capture_cancelled.emit()
                return False
            
            # 记录捕获的按键
            self.capture_signals.key_captured.emit(key_name)
            
            # 返回False停止监听
            return False
            
        except Exception as e:
            logger.error(f"处理鼠标事件失败: {e}")
            return True
    
    def accept_capture(self, key_name: str):
        """接受捕获的按键"""
        self.stop_capture()
        
        self.current_value = key_name
        self.is_capturing = False
        
        # 更新显示和样式
        self.update_display()
        self.update_input_style(False)
        
        self.value_changed.emit(key_name)
        logger.info(f"按键设置为: {key_name}")
    
    def cancel_capture(self):
        """取消捕获，恢复之前的值"""
        self.stop_capture()
        
        # 恢复之前的值
        self.current_value = self.previous_value
        self.is_capturing = False
        
        # 更新显示和样式
        self.update_display()
        self.update_input_style(False)
        
        logger.info("取消按键捕获")
    
    def stop_capture(self):
        """停止捕获按键"""
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
        except Exception as e:
            logger.error(f"停止按键捕获失败: {e}")
    
    def get_value(self) -> str:
        """获取当前值"""
        return self.current_value
    
    def set_value(self, value: str):
        """设置值"""
        self.current_value = value
        self.update_display()

