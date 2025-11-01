from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import win32gui
import os

from whimbox.common.logger import logger
from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.common.path_lib import SCRIPT_PATH
from whimbox.task.navigation_task.common import path_manager


class PathSelectionDialog(QDialog):
    """路径选择对话框"""
    path_selected = pyqtSignal(str)  # 发送选中的路径名
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(800, 800)
        
        # 搜索条件
        self.filter_target = None
        self.filter_type = None
        self.filter_count = None
        
        self.init_ui()
        self.load_paths()
    
    def init_ui(self):
        """初始化UI"""
        # 创建主容器（用于圆角背景）
        main_container = QWidget(self)
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet("""
            #mainContainer {
                background-color: #F5F5F5;
                border-radius: 12px;
            }
        """)
        
        # 主布局
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("🗺️ 自动跑图路线选择")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2196F3;
                padding: 5px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 搜索过滤区域 - 第一行：三个筛选条件平均分布
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(12)
        filter_row1.setContentsMargins(0, 8, 0, 4)
        
        # 标签样式
        label_style = "color: #424242; font-size: 16px; font-weight: bold;"
        
        # 目标素材
        target_container = QHBoxLayout()
        target_container.setSpacing(8)
        target_label = QLabel("目标素材:")
        target_label.setStyleSheet(label_style)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("输入素材名")
        self.target_input.textChanged.connect(self.on_filter_changed)
        self.target_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        target_container.addWidget(target_label)
        target_container.addWidget(self.target_input, 1)  # stretch factor = 1
        filter_row1.addLayout(target_container, 1)
        
        # 路线类型
        type_container = QHBoxLayout()
        type_container.setSpacing(8)
        type_label = QLabel("路线类型:")
        type_label.setStyleSheet(label_style)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["不限", "采集", "捕虫", "清洁", "战斗", "钓鱼", "综合"])
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 16px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        type_container.addWidget(type_label)
        type_container.addWidget(self.type_combo, 1)  # stretch factor = 1
        filter_row1.addLayout(type_container, 1)
        
        # 目标数量
        count_container = QHBoxLayout()
        count_container.setSpacing(8)
        count_label = QLabel("目标数量:")
        count_label.setStyleSheet(label_style)
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(0, 999)
        self.count_spinbox.setValue(0)
        self.count_spinbox.setSpecialValueText("不限")
        self.count_spinbox.valueChanged.connect(self.on_filter_changed)
        self.count_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 16px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #2196F3;
            }
        """)
        count_container.addWidget(count_label)
        count_container.addWidget(self.count_spinbox, 1)  # stretch factor = 1
        filter_row1.addLayout(count_container, 1)
        
        layout.addLayout(filter_row1)
        
        # 第二行：刷新和重置按钮
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(12)
        filter_row2.setContentsMargins(0, 4, 0, 8)
        filter_row2.addStretch()
        
        open_folder_button = QPushButton("📁 打开路线文件夹")
        open_folder_button.setFixedSize(150, 35)
        open_folder_button.clicked.connect(self.open_path_folder)
        open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """)
        filter_row2.addWidget(open_folder_button)
        
        refresh_button = QPushButton("🔄 刷新路线")
        refresh_button.setFixedSize(120, 35)
        refresh_button.clicked.connect(self.reload_paths)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        filter_row2.addWidget(refresh_button)
        
        reset_button = QPushButton("🗑️ 重置筛选")
        reset_button.setFixedSize(120, 35)
        reset_button.clicked.connect(self.reset_filters)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        filter_row2.addWidget(reset_button)
        
        layout.addLayout(filter_row2)
        
        # 路径列表区域 - 使用表格展示
        self.path_list = QTableWidget()
        self.path_list.setColumnCount(5)
        self.path_list.setHorizontalHeaderLabels(["路线名", "类型", "目标", "数量", "区域"])
        
        # 表格属性设置
        self.path_list.setSelectionBehavior(QTableWidget.SelectRows)  # 选择整行
        self.path_list.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.path_list.setEditTriggers(QTableWidget.NoEditTriggers)  # 不可编辑
        self.path_list.verticalHeader().setVisible(False)  # 隐藏行号
        self.path_list.setFocusPolicy(Qt.NoFocus)  # 移除焦点虚线框
        
        # 列宽设置
        header = self.path_list.horizontalHeader()
        
        # 第0列自动拉伸占据剩余宽度
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # 其他列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.path_list.setColumnWidth(1, 100)  # 类型
        self.path_list.setColumnWidth(2, 120)  # 目标
        self.path_list.setColumnWidth(3, 80)   # 数量
        self.path_list.setColumnWidth(4, 120)  # 区域
        
        # 表格样式
        self.path_list.setStyleSheet("""
            QTableWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                font-size: 16px;
                gridline-color: #DEDEDE;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
                border: none;
                outline: none;
            }
            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 4px;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background-color: #F5F5F5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9E9E9E;
            }
        """)
        
        # 连接信号
        self.path_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.path_list, 1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.start_button = QPushButton("🚀 开始跑图")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #E0E0E0;
            }
        """)
        self.start_button.setEnabled(False)
        
        self.delete_button = QPushButton("🗑️ 删除路线")
        self.delete_button.setFixedHeight(40)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
            QPushButton:pressed {
                background-color: #D84315;
            }
            QPushButton:disabled {
                background-color: #FFCCBC;
                color: #E0E0E0;
            }
        """)
        
        cancel_button = QPushButton("取消")
        cancel_button.setFixedHeight(40)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c2170a;
            }
        """)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # 设置主容器大小和位置
        main_container.setFixedSize(800, 800)
        
        # 创建对话框布局
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_container)
    
    def open_path_folder(self):
        """打开路线文件夹"""
        res, msg = path_manager.open_path_folder()
        if not res:
            QMessageBox.warning(self, "提示", msg)
    
    def reload_paths(self):
        """刷新路径列表"""
        path_manager.init_path_dict()
        self.load_paths()
        self.reset_filters()

    def load_paths(self):
        """加载路径列表"""
        try:
            # 获取筛选条件
            target = self.filter_target if self.filter_target else None
            path_type = self.filter_type if self.filter_type else None
            count = self.filter_count if self.filter_count and self.filter_count > 0 else None
            
            # 查询路径
            paths = path_manager.query_path(target=target, type=path_type, count=count)
            
            # 清空表格
            self.path_list.setRowCount(0)
            
            if not paths:
                # 添加一行提示信息
                self.path_list.setRowCount(1)
                no_data_item = QTableWidgetItem("未找到符合条件的路线")
                no_data_item.setFlags(Qt.NoItemFlags)  # 不可选择
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.path_list.setItem(0, 0, no_data_item)
                self.path_list.setSpan(0, 0, 1, 5)  # 合并所有列
                return
            
            # 添加路径到表格
            for row, path_record in enumerate(paths):
                self.path_list.insertRow(row)
                
                info = path_record.info
                
                # 路线名
                name_item = QTableWidgetItem(info.name or "-")
                name_item.setData(Qt.UserRole, path_record)  # 存储完整的路径记录
                self.path_list.setItem(row, 0, name_item)
                
                # 类型（带图标）
                type_text = info.type or "-"
                if info.type:
                    type_icons = {
                        "采集": "🌿",
                        "捕虫": "🦋",
                        "清洁": "✨",
                        "战斗": "⚔️",
                        "钓鱼": "🎣",
                        "综合": "🎯"
                    }
                    icon = type_icons.get(info.type, "📋")
                    type_text = f"{icon} {info.type}"
                type_item = QTableWidgetItem(type_text)
                type_item.setTextAlignment(Qt.AlignCenter)
                self.path_list.setItem(row, 1, type_item)
                
                # 目标
                target_item = QTableWidgetItem(info.target or "-")
                self.path_list.setItem(row, 2, target_item)
                
                # 数量
                count_text = str(info.count) if info.count else "-"
                count_item = QTableWidgetItem(count_text)
                count_item.setTextAlignment(Qt.AlignCenter)
                self.path_list.setItem(row, 3, count_item)
                
                # 区域
                region_text = info.region or info.map or "-"
                region_item = QTableWidgetItem(region_text)
                self.path_list.setItem(row, 4, region_item)
            
            logger.info(f"Loaded {len(paths)} paths matching criteria")
            
        except Exception as e:
            logger.error(f"Failed to load paths: {e}")
            self.path_list.setRowCount(1)
            error_item = QTableWidgetItem(f"加载路线失败: {str(e)}")
            error_item.setFlags(Qt.NoItemFlags)
            error_item.setTextAlignment(Qt.AlignCenter)
            self.path_list.setItem(0, 0, error_item)
            self.path_list.setSpan(0, 0, 1, 5)  # 合并所有列
    
    
    def on_filter_changed(self):
        """筛选条件改变时"""
        # 更新筛选条件
        self.filter_target = self.target_input.text().strip() or None
        
        type_text = self.type_combo.currentText()
        self.filter_type = type_text if type_text != "不限" else None
        
        count_value = self.count_spinbox.value()
        self.filter_count = count_value if count_value > 0 else None
        
        # 重新加载路径列表
        self.load_paths()
    
    def reset_filters(self):
        """重置所有筛选条件"""
        self.target_input.clear()
        self.type_combo.setCurrentIndex(0)  # 设置为"不限"
        self.count_spinbox.setValue(0)  # 设置为"不限"
        logger.info("Filters reset")
    
    def on_selection_changed(self):
        """选择改变时"""
        selected_items = self.path_list.selectedItems()
        if selected_items:
            # 获取选中行的第一列（路线名）
            row = self.path_list.currentRow()
            if row >= 0:
                name_item = self.path_list.item(row, 0)
                if name_item and name_item.data(Qt.UserRole):
                    self.start_button.setEnabled(True)
                    self.delete_button.setEnabled(True)
                    return
        self.start_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def on_start_clicked(self):
        """点击开始按钮"""
        row = self.path_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条路线")
            return
        
        name_item = self.path_list.item(row, 0)
        if not name_item:
            return
        
        path_record = name_item.data(Qt.UserRole)
        if not path_record:
            return
        
        logger.info(f"Selected path: {path_record.info.name}")
        self.path_selected.emit(path_record.info.name)
        self.accept()
    
    def on_delete_clicked(self):
        """点击删除按钮"""
        row = self.path_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条路线")
            return
        
        name_item = self.path_list.item(row, 0)
        if not name_item:
            return
        
        path_record = name_item.data(Qt.UserRole)
        if not path_record:
            return
        
        path_name = path_record.info.name
        
        # 弹出确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除路线「{path_name}」吗？\n（订阅路线请在路线订阅网站取消订阅来删除）",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 调用 PathManager 的删除方法
        deleted_count = path_manager.delete_path(path_name)
        
        if deleted_count > 0:
            QMessageBox.information(self, "成功", f"已删除路线「{path_name}」")
            # 重新加载路径列表
            self.reload_paths()
        else:
            QMessageBox.warning(self, "提示", f"未找到路线「{path_name}」的文件")
    
    def show_centered(self):
        """在游戏窗口中央显示对话框"""
        if HANDLE_OBJ.get_handle():
            try:
                # 获取游戏窗口的位置和大小
                game_rect = win32gui.GetWindowRect(HANDLE_OBJ.get_handle())
                game_x, game_y, game_right, game_bottom = game_rect
                game_width = game_right - game_x
                game_height = game_bottom - game_y
                
                # 计算对话框居中位置
                dialog_x = game_x + (game_width - self.width()) // 2
                dialog_y = game_y + (game_height - self.height()) // 2
                
                self.move(dialog_x, dialog_y)
            except Exception as e:
                logger.error(f"Failed to center dialog: {e}")
                # 如果失败，使用屏幕居中
                screen = QApplication.desktop().screenGeometry()
                self.move((screen.width() - self.width()) // 2,
                         (screen.height() - self.height()) // 2)
        else:
            # 没有游戏窗口时使用屏幕居中
            screen = QApplication.desktop().screenGeometry()
            self.move((screen.width() - self.width()) // 2,
                     (screen.height() - self.height()) // 2)
        
        self.show()
        self.raise_()
        self.activateWindow()

