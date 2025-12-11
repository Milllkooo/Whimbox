from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os

from whimbox.common.logger import logger
from whimbox.common.scripts_manager import scripts_manager


class MacroSelectionDialog(QDialog):
    """宏选择对话框"""
    macro_selected = pyqtSignal(str)  # 发送选中的宏名
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(600, 700)
        
        # 搜索条件
        self.filter_name = None
        
        self.init_ui()
        self.load_macros()
    
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
        title_label = QLabel("🎬 宏选择")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: bold;
                color: #2196F3;
                padding: 5px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 搜索过滤区域 - 第一行：宏名称搜索框
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(12)
        filter_row1.setContentsMargins(0, 8, 0, 4)
        
        # 标签样式
        label_style = "color: #424242; font-size: 8pt; font-weight: bold;"
        
        # 宏名称
        name_container = QHBoxLayout()
        name_container.setSpacing(8)
        name_label = QLabel("宏名称:")
        name_label.setStyleSheet(label_style)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入宏名称")
        self.name_input.textChanged.connect(self.on_filter_changed)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 8pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        name_container.addWidget(name_label)
        name_container.addWidget(self.name_input, 1)  # stretch factor = 1
        filter_row1.addLayout(name_container)
        
        layout.addLayout(filter_row1)
        
        # 第二行：刷新和重置按钮
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(12)
        filter_row2.setContentsMargins(0, 4, 0, 8)
        filter_row2.addStretch()
        
        open_folder_button = QPushButton("📁 打开宏文件夹")
        open_folder_button.setFixedSize(140, 35)
        open_folder_button.clicked.connect(self.open_macro_folder)
        open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 8pt;
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
        
        refresh_button = QPushButton("🔄 刷新宏")
        refresh_button.setFixedSize(110, 35)
        refresh_button.clicked.connect(self.reload_macros)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 8pt;
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
                font-size: 8pt;
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
        
        # 宏列表区域 - 使用表格展示
        self.macro_list = QTableWidget()
        self.macro_list.setColumnCount(1)
        self.macro_list.setHorizontalHeaderLabels(["宏名称"])
        
        # 表格属性设置
        self.macro_list.setSelectionBehavior(QTableWidget.SelectRows)  # 选择整行
        self.macro_list.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.macro_list.setEditTriggers(QTableWidget.NoEditTriggers)  # 不可编辑
        self.macro_list.verticalHeader().setVisible(False)  # 隐藏行号
        self.macro_list.setFocusPolicy(Qt.NoFocus)  # 移除焦点虚线框
        
        # 列宽设置
        header = self.macro_list.horizontalHeader()
        
        # 第0列自动拉伸占据剩余宽度
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # 表格样式
        self.macro_list.setStyleSheet("""
            QTableWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                font-size: 8pt;
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
                font-size: 8pt;
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
        self.macro_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.macro_list, 1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.start_button = QPushButton("🚀 运行宏")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 7pt;
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
        
        self.delete_button = QPushButton("🗑️ 删除宏")
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
                font-size: 7pt;
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
                font-size: 7pt;
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
        main_container.setFixedSize(600, 700)
        
        # 创建对话框布局
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_container)
    
    def open_macro_folder(self):
        """打开宏文件夹"""
        res, msg = scripts_manager.open_macro_folder()
        if not res:
            QMessageBox.warning(self, "提示", msg)
    
    def reload_macros(self):
        """刷新宏列表"""
        scripts_manager.init_scripts_dict()
        self.load_macros()
        self.reset_filters()

    def load_macros(self):
        """加载宏列表"""
        try:
            # 获取筛选条件
            name = self.filter_name if self.filter_name else None
            
            # 查询宏
            macros = scripts_manager.query_macro(name=name)
            
            # 清空表格
            self.macro_list.setRowCount(0)
            
            if not macros:
                # 添加一行提示信息
                self.macro_list.setRowCount(1)
                no_data_item = QTableWidgetItem("未找到符合条件的宏")
                no_data_item.setFlags(Qt.NoItemFlags)  # 不可选择
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.macro_list.setItem(0, 0, no_data_item)
                return
            
            # 添加宏到表格
            for row, macro_record in enumerate(macros):
                self.macro_list.insertRow(row)
                
                info = macro_record.info
                
                # 宏名称
                name_item = QTableWidgetItem(info.name or "-")
                name_item.setData(Qt.UserRole, macro_record)  # 存储完整的宏记录
                self.macro_list.setItem(row, 0, name_item)
            
            logger.info(f"Loaded {len(macros)} macros matching criteria")
            
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")
            self.macro_list.setRowCount(1)
            error_item = QTableWidgetItem(f"加载宏失败: {str(e)}")
            error_item.setFlags(Qt.NoItemFlags)
            error_item.setTextAlignment(Qt.AlignCenter)
            self.macro_list.setItem(0, 0, error_item)
    
    
    def on_filter_changed(self):
        """筛选条件改变时"""
        # 更新筛选条件
        self.filter_name = self.name_input.text().strip() or None
        
        # 重新加载宏列表
        self.load_macros()
    
    def reset_filters(self):
        """重置所有筛选条件"""
        self.name_input.clear()
        logger.info("Filters reset")
    
    def on_selection_changed(self):
        """选择改变时"""
        selected_items = self.macro_list.selectedItems()
        if selected_items:
            # 获取选中行的第一列（宏名称）
            row = self.macro_list.currentRow()
            if row >= 0:
                name_item = self.macro_list.item(row, 0)
                if name_item and name_item.data(Qt.UserRole):
                    self.start_button.setEnabled(True)
                    self.delete_button.setEnabled(True)
                    return
        self.start_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def on_start_clicked(self):
        """点击开始按钮"""
        row = self.macro_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个宏")
            return
        
        name_item = self.macro_list.item(row, 0)
        if not name_item:
            return
        
        macro_record = name_item.data(Qt.UserRole)
        if not macro_record:
            return
        
        logger.info(f"Selected macro: {macro_record.info.name}")
        self.macro_selected.emit(macro_record.info.name)
        self.accept()
    
    def on_delete_clicked(self):
        """点击删除按钮"""
        row = self.macro_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个宏")
            return
        
        name_item = self.macro_list.item(row, 0)
        if not name_item:
            return
        
        macro_record = name_item.data(Qt.UserRole)
        if not macro_record:
            return
        
        macro_name = macro_record.info.name
        
        # 弹出确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除宏「{macro_name}」吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 调用 ScriptsManager 的删除方法
        deleted_count = scripts_manager.delete_macro(macro_name)
        
        if deleted_count > 0:
            QMessageBox.information(self, "成功", f"已删除宏「{macro_name}」")
            # 重新加载宏列表
            self.reload_macros()
        else:
            QMessageBox.warning(self, "提示", f"未找到宏「{macro_name}」的文件")
    
    def show_centered(self):
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2,
                    (screen.height() - self.height()) // 2)
        
        self.show()
        self.raise_()
        self.activateWindow()

