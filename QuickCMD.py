#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键命令 QuickCmd
快速命令执行工具
"""

import sys
import subprocess
import platform
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QTabWidget, QScrollArea, QMessageBox, QGroupBox,
                             QGridLayout, QDialog, QLineEdit, QDialogButtonBox,
                             QListWidget, QListWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

class CommandExecutor(QThread):
    """后台执行命令的线程"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        try:
            # Windows 需要设置编码
            if platform.system() == "Windows":
                # 使用 gbk 编码处理中文
                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='gbk',
                    errors='ignore',
                    bufsize=1
                )
            else:
                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            
            # 实时读取输出
            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                self.output_signal.emit(line.rstrip())
            
            for line in process.stderr:
                output_lines.append(line)
                self.output_signal.emit(line.rstrip())
            
            process.wait(timeout=30)
            
            if not output_lines:
                self.output_signal.emit("✅ 命令执行成功！")
            
            self.finished_signal.emit(process.returncode == 0)
        except subprocess.TimeoutExpired:
            self.output_signal.emit("⚠️ 命令执行超时")
            self.finished_signal.emit(False)
        except Exception as e:
            self.output_signal.emit(f"❌ 错误: {str(e)}")
            self.finished_signal.emit(False)


class AddCommandDialog(QDialog):
    """添加/编辑自定义命令对话框"""
    def __init__(self, parent=None, edit_mode=False, command_data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑命令" if edit_mode else "添加自定义命令")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.edit_mode = edit_mode
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 命令名称
        name_label = QLabel("📝 命令名称:")
        name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 清理系统垃圾")
        self.name_input.setStyleSheet("padding: 8px; font-size: 13px; border: 2px solid #ddd; border-radius: 5px;")
        layout.addWidget(self.name_input)
        
        # 命令内容
        cmd_label = QLabel("💻 命令内容:")
        cmd_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(cmd_label)
        
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("例如: ping -n {count} {host}\n\n支持变量: 使用 {变量名} 格式")
        self.command_input.setMaximumHeight(100)
        self.command_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.command_input)
        
        # 变量列表
        var_label = QLabel("🔧 变量配置 (可选):")
        var_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(var_label)
        
        # 变量管理区域
        var_container = QWidget()
        var_layout = QVBoxLayout(var_container)
        var_layout.setContentsMargins(0, 0, 0, 0)
        
        # 变量列表
        self.var_list = QListWidget()
        self.var_list.setMaximumHeight(120)
        self.var_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        var_layout.addWidget(self.var_list)
        
        # 变量操作按钮
        var_btn_layout = QHBoxLayout()
        
        add_var_btn = QPushButton("➕ 添加变量")
        add_var_btn.setMaximumWidth(120)
        add_var_btn.clicked.connect(self.add_variable)
        var_btn_layout.addWidget(add_var_btn)
        
        edit_var_btn = QPushButton("✏️ 编辑变量")
        edit_var_btn.setMaximumWidth(120)
        edit_var_btn.clicked.connect(self.edit_variable)
        var_btn_layout.addWidget(edit_var_btn)
        
        del_var_btn = QPushButton("🗑️ 删除变量")
        del_var_btn.setMaximumWidth(120)
        del_var_btn.clicked.connect(self.delete_variable)
        var_btn_layout.addWidget(del_var_btn)
        
        var_btn_layout.addStretch()
        var_layout.addLayout(var_btn_layout)
        
        layout.addWidget(var_container)
        
        # 说明文本
        help_text = QLabel(
            "💡 提示:\n"
            "• 在命令中使用 {变量名} 来引用变量\n"
            "• 执行时会弹出对话框让你输入变量值\n"
            "• 例如: ping -n {次数} {主机地址}"
        )
        help_text.setStyleSheet("""
            QLabel {
                background: #f0f9ff;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #3b82f6;
                color: #1e40af;
                font-size: 12px;
            }
        """)
        layout.addWidget(help_text)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # 如果是编辑模式，加载数据
        if edit_mode and command_data:
            self.name_input.setText(command_data.get('name', ''))
            self.command_input.setPlainText(command_data.get('command', ''))
            for var in command_data.get('variables', []):
                self.add_variable_to_list(var)
    
    def add_variable(self):
        """添加变量"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加变量")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("变量名:"))
        var_name = QLineEdit()
        var_name.setPlaceholderText("例如: host, count, path")
        layout.addWidget(var_name)
        
        layout.addWidget(QLabel("描述:"))
        var_desc = QLineEdit()
        var_desc.setPlaceholderText("例如: 主机地址")
        layout.addWidget(var_desc)
        
        layout.addWidget(QLabel("默认值 (可选):"))
        var_default = QLineEdit()
        var_default.setPlaceholderText("例如: www.baidu.com")
        layout.addWidget(var_default)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if var_name.text():
                var_data = {
                    'name': var_name.text(),
                    'description': var_desc.text(),
                    'default': var_default.text()
                }
                self.add_variable_to_list(var_data)
    
    def add_variable_to_list(self, var_data):
        """添加变量到列表"""
        item_text = f"{var_data['name']}"
        if var_data.get('description'):
            item_text += f" - {var_data['description']}"
        if var_data.get('default'):
            item_text += f" (默认: {var_data['default']})"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, var_data)
        self.var_list.addItem(item)
    
    def edit_variable(self):
        """编辑选中的变量"""
        current_item = self.var_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要编辑的变量")
            return
        
        var_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑变量")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("变量名:"))
        var_name = QLineEdit(var_data['name'])
        layout.addWidget(var_name)
        
        layout.addWidget(QLabel("描述:"))
        var_desc = QLineEdit(var_data.get('description', ''))
        layout.addWidget(var_desc)
        
        layout.addWidget(QLabel("默认值 (可选):"))
        var_default = QLineEdit(var_data.get('default', ''))
        layout.addWidget(var_default)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_var_data = {
                'name': var_name.text(),
                'description': var_desc.text(),
                'default': var_default.text()
            }
            current_item.setData(Qt.ItemDataRole.UserRole, new_var_data)
            
            item_text = f"{new_var_data['name']}"
            if new_var_data.get('description'):
                item_text += f" - {new_var_data['description']}"
            if new_var_data.get('default'):
                item_text += f" (默认: {new_var_data['default']})"
            current_item.setText(item_text)
    
    def delete_variable(self):
        """删除选中的变量"""
        current_item = self.var_list.currentItem()
        if current_item:
            self.var_list.takeItem(self.var_list.row(current_item))
    
    def get_command(self):
        variables = []
        for i in range(self.var_list.count()):
            item = self.var_list.item(i)
            variables.append(item.data(Qt.ItemDataRole.UserRole))
        
        return {
            'name': self.name_input.text(),
            'command': self.command_input.toPlainText(),
            'variables': variables
        }


class LetYouHandApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_os = platform.system()
        self.dark_mode = False
        self.custom_commands = self.load_custom_commands()
        self.init_ui()
    
    def load_custom_commands(self):
        """加载自定义命令"""
        config_file = 'custom_commands.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_custom_commands(self):
        """保存自定义命令"""
        with open('custom_commands.json', 'w', encoding='utf-8') as f:
            json.dump(self.custom_commands, f, ensure_ascii=False, indent=2)
    
    def get_light_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f4f8, stop:1 #d9e2ec);
            }
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 12px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3e8ef, stop:1 #d0d7de);
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2563eb;
            }
            QTabBar::tab:hover {
                background: #f8fafc;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                padding: 14px 20px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
            QPushButton:pressed {
                background: #1e40af;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #1f2937;
            }
            QTextEdit {
                background-color: #1e293b;
                color: #10b981;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 10px;
                padding: 12px;
                border: 2px solid #334155;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """
    
    def get_dark_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
            }
            QTabWidget::pane {
                border: none;
                background: #1e293b;
                border-radius: 12px;
            }
            QTabBar::tab {
                background: #334155;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1e293b;
                color: #60a5fa;
            }
            QTabBar::tab:hover {
                background: #475569;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                padding: 14px 20px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #3b82f6);
            }
            QPushButton:pressed {
                background: #1e40af;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #334155;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                background: #1e293b;
                color: #e2e8f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #e2e8f0;
            }
            QTextEdit {
                background-color: #0f172a;
                color: #10b981;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 10px;
                padding: 12px;
                border: 2px solid #1e293b;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QLabel {
                color: #e2e8f0;
            }
        """
    
    def init_ui(self):
        self.setWindowTitle("一键命令 QuickCmd v1.0 build 00001")
        self.setGeometry(100, 100, 1000, 750)
        self.setStyleSheet(self.get_light_theme())
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        
        # 顶部栏
        top_bar = QHBoxLayout()
        
        # 标题
        title_layout = QHBoxLayout()
        
        # 中文标题
        title_cn = QLabel("一键命令")
        title_cn.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_cn.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.5 #8b5cf6, stop:1 #ec4899);
                padding: 10px 5px;
                letter-spacing: 3px;
            }
        """)
        title_layout.addWidget(title_cn)
        
        # 英文标题
        title_en = QLabel("QuickCmd")
        title_en.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        title_en.setStyleSheet("""
            QLabel {
                color: #64748b;
                padding: 10px 5px;
                font-style: italic;
            }
        """)
        title_layout.addWidget(title_en)
        
        title_layout.addStretch()
        top_bar.addLayout(title_layout)
        
        # 系统信息
        os_label = QLabel(f"系统: {self.current_os}")
        os_label.setStyleSheet("color: #64748b; padding: 5px; font-size: 13px;")
        top_bar.addWidget(os_label)
        
        # 主题切换按钮
        self.theme_btn = QPushButton("🌙 夜间模式")
        self.theme_btn.setMaximumWidth(120)
        self.theme_btn.setMinimumHeight(35)
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_btn)
        
        layout.addLayout(top_bar)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_windows_tab(), "🪟 Windows")
        self.tabs.addTab(self.create_linux_tab(), "🐧 Linux")
        self.tabs.addTab(self.create_mac_tab(), "🍎 macOS")
        self.tabs.addTab(self.create_custom_tab(), "⚡ 自定义命令")
        
        # 根据当前系统选择默认标签
        if self.current_os == "Windows":
            self.tabs.setCurrentIndex(0)
        elif self.current_os == "Linux":
            self.tabs.setCurrentIndex(1)
        elif self.current_os == "Darwin":
            self.tabs.setCurrentIndex(2)
        
        layout.addWidget(self.tabs)
        
        # 输出区域
        output_header = QHBoxLayout()
        output_label = QLabel("📋 执行结果")
        output_label.setStyleSheet("font-weight: bold; padding: 5px; font-size: 13px;")
        output_header.addWidget(output_label)
        
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setMaximumWidth(80)
        clear_btn.setMinimumHeight(30)
        clear_btn.clicked.connect(lambda: self.output_text.clear())
        output_header.addWidget(clear_btn)
        
        layout.addLayout(output_header)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        layout.addWidget(self.output_text)
    
    def toggle_theme(self):
        """切换主题"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(self.get_dark_theme())
            self.theme_btn.setText("☀️ 日间模式")
        else:
            self.setStyleSheet(self.get_light_theme())
            self.theme_btn.setText("🌙 夜间模式")
    
    def create_windows_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 系统信息类
        sys_group = QGroupBox("📊 系统信息")
        sys_layout = QGridLayout()
        sys_layout.setSpacing(10)
        commands = [
            ("💻 系统详情", "systeminfo | findstr /C:\"OS\" /C:\"系统\""),
            ("🌐 IP配置", "ipconfig /all"),
            ("💾 磁盘空间", "wmic logicaldisk get name,size,freespace,filesystem"),
            ("⚙️ 进程列表", "tasklist"),
            ("🔋 电源状态", "powercfg /batteryreport /output battery.html & echo 报告已生成"),
            ("📈 性能监控", "wmic cpu get loadpercentage"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            sys_layout.addWidget(btn, i // 3, i % 3)
        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)
        
        # 网络管理类
        net_group = QGroupBox("🌐 网络管理")
        net_layout = QGridLayout()
        net_layout.setSpacing(10)
        commands = [
            ("🔍 测试百度", "ping -n 4 www.baidu.com"),
            ("🔍 测试谷歌", "ping -n 4 www.google.com"),
            ("📡 网络连接", "netstat -ano"),
            ("🔄 刷新DNS", "ipconfig /flushdns"),
            ("🗺️ 路由表", "route print"),
            ("📶 WiFi信息", "netsh wlan show profiles"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            net_layout.addWidget(btn, i // 3, i % 3)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        # 文件管理类
        file_group = QGroupBox("📁 文件管理")
        file_layout = QGridLayout()
        file_layout.setSpacing(10)
        commands = [
            ("📂 打开资源管理器", "explorer ."),
            ("🗑️ 清理临时文件", "del /q /f /s %TEMP%\\* 2>nul"),
            ("📋 当前目录", "dir"),
            ("🪟 系统目录", "explorer C:\\Windows"),
            ("👤 用户目录", "explorer %USERPROFILE%"),
            ("📥 下载目录", "explorer %USERPROFILE%\\Downloads"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            file_layout.addWidget(btn, i // 3, i % 3)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 系统工具类
        tool_group = QGroupBox("🛠️ 系统工具")
        tool_layout = QGridLayout()
        tool_layout.setSpacing(10)
        commands = [
            ("🔧 任务管理器", "taskmgr"),
            ("⚙️ 控制面板", "control"),
            ("🖥️ 设备管理器", "devmgmt.msc"),
            ("📊 资源监视器", "resmon"),
            ("🔐 注册表编辑器", "regedit"),
            ("🧹 磁盘清理", "cleanmgr"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            tool_layout.addWidget(btn, i // 3, i % 3)
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)
        
        layout.addStretch()
        return scroll
    
    def create_linux_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 系统信息类
        sys_group = QGroupBox("📊 系统信息")
        sys_layout = QGridLayout()
        sys_layout.setSpacing(10)
        commands = [
            ("💻 系统信息", "uname -a"),
            ("🧠 内存使用", "free -h"),
            ("💾 磁盘空间", "df -h"),
            ("⚙️ CPU信息", "lscpu | head -25"),
            ("📊 系统负载", "uptime"),
            ("🔋 电池状态", "upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>/dev/null || echo '无电池信息'"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            sys_layout.addWidget(btn, i // 3, i % 3)
        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)
        
        # 网络管理类
        net_group = QGroupBox("🌐 网络管理")
        net_layout = QGridLayout()
        net_layout.setSpacing(10)
        commands = [
            ("🔍 测试百度", "ping -c 4 www.baidu.com"),
            ("🔍 测试谷歌", "ping -c 4 www.google.com"),
            ("📡 网络接口", "ip addr show"),
            ("🔗 网络连接", "ss -tuln"),
            ("🗺️ 路由表", "ip route"),
            ("📶 WiFi信息", "nmcli dev wifi list 2>/dev/null || iwconfig 2>/dev/null"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            net_layout.addWidget(btn, i // 3, i % 3)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        # 进程管理类
        proc_group = QGroupBox("⚙️ 进程管理")
        proc_layout = QGridLayout()
        proc_layout.setSpacing(10)
        commands = [
            ("📋 进程列表", "ps aux | head -25"),
            ("📈 系统负载", "top -bn1 | head -20"),
            ("🔌 端口占用", "netstat -tulpn 2>/dev/null || ss -tulpn"),
            ("🔧 系统服务", "systemctl list-units --type=service --state=running | head -25"),
            ("💾 磁盘IO", "iostat 2>/dev/null || echo '请安装 sysstat'"),
            ("🌡️ 系统温度", "sensors 2>/dev/null || echo '请安装 lm-sensors'"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            proc_layout.addWidget(btn, i // 3, i % 3)
        proc_group.setLayout(proc_layout)
        layout.addWidget(proc_group)
        
        # 文件管理类
        file_group = QGroupBox("📁 文件管理")
        file_layout = QGridLayout()
        file_layout.setSpacing(10)
        commands = [
            ("📂 当前目录", "ls -lah"),
            ("🔍 大文件查找", "du -h --max-depth=1 | sort -hr | head -10"),
            ("🗑️ 清理缓存", "sudo apt clean 2>/dev/null || sudo yum clean all 2>/dev/null || echo '请手动清理'"),
            ("👤 用户目录", "cd ~ && pwd && ls -lah"),
            ("📊 目录大小", "du -sh * | sort -hr | head -10"),
            ("🔎 最近文件", "find . -type f -mtime -1 2>/dev/null | head -20"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            file_layout.addWidget(btn, i // 3, i % 3)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        layout.addStretch()
        return scroll
    
    def create_mac_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 系统信息类
        sys_group = QGroupBox("📊 系统信息")
        sys_layout = QGridLayout()
        sys_layout.setSpacing(10)
        commands = [
            ("💻 系统信息", "system_profiler SPSoftwareDataType"),
            ("🧠 内存使用", "vm_stat"),
            ("💾 磁盘空间", "df -h"),
            ("⚙️ CPU信息", "sysctl -n machdep.cpu.brand_string"),
            ("📊 系统负载", "uptime"),
            ("🔋 电池状态", "pmset -g batt"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            sys_layout.addWidget(btn, i // 3, i % 3)
        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)
        
        # 网络管理类
        net_group = QGroupBox("🌐 网络管理")
        net_layout = QGridLayout()
        net_layout.setSpacing(10)
        commands = [
            ("🔍 测试百度", "ping -c 4 www.baidu.com"),
            ("🔍 测试谷歌", "ping -c 4 www.google.com"),
            ("📡 网络接口", "ifconfig"),
            ("🔗 网络连接", "netstat -an"),
            ("🗺️ 路由表", "netstat -nr"),
            ("📶 WiFi信息", "networksetup -listallhardwareports"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            net_layout.addWidget(btn, i // 3, i % 3)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        # 进程管理类
        proc_group = QGroupBox("⚙️ 进程管理")
        proc_layout = QGridLayout()
        proc_layout.setSpacing(10)
        commands = [
            ("📋 进程列表", "ps aux | head -25"),
            ("📈 系统监控", "top -l 1 | head -20"),
            ("🔌 端口占用", "lsof -i -P"),
            ("🔧 启动项", "launchctl list | head -25"),
            ("💾 磁盘IO", "iostat"),
            ("🌡️ 系统温度", "sudo powermetrics --samplers smc | head -20"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            proc_layout.addWidget(btn, i // 3, i % 3)
        proc_group.setLayout(proc_layout)
        layout.addWidget(proc_group)
        
        # 文件管理类
        file_group = QGroupBox("📁 文件管理")
        file_layout = QGridLayout()
        file_layout.setSpacing(10)
        commands = [
            ("📂 打开Finder", "open ."),
            ("📋 当前目录", "ls -lah"),
            ("🔍 大文件查找", "du -h -d 1 | sort -hr | head -10"),
            ("👤 用户目录", "open ~"),
            ("📥 下载目录", "open ~/Downloads"),
            ("🗑️ 清空废纸篓", "rm -rf ~/.Trash/*"),
        ]
        for i, (name, cmd) in enumerate(commands):
            btn = self.create_command_button(name, cmd)
            file_layout.addWidget(btn, i // 3, i % 3)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        layout.addStretch()
        return scroll
    
    def create_custom_tab(self):
        """创建自定义命令标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 顶部按钮栏
        top_bar = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加命令")
        add_btn.setMaximumWidth(150)
        add_btn.clicked.connect(self.add_custom_command)
        top_bar.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 刷新列表")
        refresh_btn.setMaximumWidth(150)
        refresh_btn.clicked.connect(self.refresh_custom_commands)
        top_bar.addWidget(refresh_btn)
        
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # 自定义命令列表
        self.custom_group = QGroupBox("⚡ 我的自定义命令")
        self.custom_layout = QGridLayout()
        self.custom_layout.setSpacing(10)
        self.custom_group.setLayout(self.custom_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.custom_group)
        layout.addWidget(scroll)
        
        # 加载自定义命令
        self.refresh_custom_commands()
        
        return widget
    
    def add_custom_command(self):
        """添加自定义命令"""
        dialog = AddCommandDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cmd_data = dialog.get_command()
            if cmd_data['name'] and cmd_data['command']:
                self.custom_commands.append(cmd_data)
                self.save_custom_commands()
                self.refresh_custom_commands()
                QMessageBox.information(self, "成功", f"已添加命令: {cmd_data['name']}")
            else:
                QMessageBox.warning(self, "错误", "命令名称和内容不能为空！")
    
    def refresh_custom_commands(self):
        """刷新自定义命令列表"""
        # 清空现有按钮
        for i in reversed(range(self.custom_layout.count())): 
            widget = self.custom_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 添加自定义命令按钮
        if not self.custom_commands:
            label = QLabel("暂无自定义命令\n点击上方'添加命令'按钮创建你的第一个命令！")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #94a3b8; padding: 50px; font-size: 14px;")
            self.custom_layout.addWidget(label, 0, 0, 1, 3)
        else:
            for i, cmd_data in enumerate(self.custom_commands):
                btn_layout = QHBoxLayout()
                
                # 执行按钮
                has_vars = len(cmd_data.get('variables', [])) > 0
                btn_text = f"⚡ {cmd_data['name']}"
                if has_vars:
                    btn_text += " 📝"
                
                exec_btn = QPushButton(btn_text)
                exec_btn.clicked.connect(lambda checked, idx=i: self.execute_custom_command(idx))
                exec_btn.setToolTip(f"命令: {cmd_data['command']}")
                exec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_layout.addWidget(exec_btn, 3)
                
                # 编辑按钮
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(50)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #10b981, stop:1 #059669);
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #059669, stop:1 #047857);
                    }
                """)
                edit_btn.clicked.connect(lambda checked, idx=i: self.edit_custom_command(idx))
                btn_layout.addWidget(edit_btn, 1)
                
                # 删除按钮
                del_btn = QPushButton("🗑️")
                del_btn.setMaximumWidth(50)
                del_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ef4444, stop:1 #dc2626);
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #dc2626, stop:1 #b91c1c);
                    }
                """)
                del_btn.clicked.connect(lambda checked, idx=i: self.delete_custom_command(idx))
                btn_layout.addWidget(del_btn, 1)
                
                container = QWidget()
                container.setLayout(btn_layout)
                self.custom_layout.addWidget(container, i // 2, i % 2)
    
    def execute_custom_command(self, index):
        """执行自定义命令"""
        if 0 <= index < len(self.custom_commands):
            cmd_data = self.custom_commands[index]
            command = cmd_data['command']
            variables = cmd_data.get('variables', [])
            
            # 如果有变量，弹出输入对话框
            if variables:
                var_values = {}
                for var in variables:
                    dialog = QDialog(self)
                    dialog.setWindowTitle(f"输入变量: {var['name']}")
                    dialog.setModal(True)
                    dialog.setMinimumWidth(400)
                    
                    layout = QVBoxLayout(dialog)
                    
                    # 变量描述
                    if var.get('description'):
                        desc_label = QLabel(f"📝 {var['description']}")
                        desc_label.setStyleSheet("font-size: 13px; color: #64748b; padding: 5px;")
                        layout.addWidget(desc_label)
                    
                    # 输入框
                    input_label = QLabel(f"请输入 {var['name']} 的值:")
                    input_label.setStyleSheet("font-weight: bold;")
                    layout.addWidget(input_label)
                    
                    var_input = QLineEdit()
                    if var.get('default'):
                        var_input.setText(var['default'])
                        var_input.setPlaceholderText(f"默认: {var['default']}")
                    var_input.setStyleSheet("padding: 8px; font-size: 13px;")
                    layout.addWidget(var_input)
                    
                    buttons = QDialogButtonBox(
                        QDialogButtonBox.StandardButton.Ok | 
                        QDialogButtonBox.StandardButton.Cancel
                    )
                    buttons.accepted.connect(dialog.accept)
                    buttons.rejected.connect(dialog.reject)
                    layout.addWidget(buttons)
                    
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        var_values[var['name']] = var_input.text() or var.get('default', '')
                    else:
                        return  # 用户取消
                
                # 替换命令中的变量
                for var_name, var_value in var_values.items():
                    command = command.replace(f"{{{var_name}}}", var_value)
            
            self.execute_command(command, cmd_data['name'])
    
    def edit_custom_command(self, index):
        """编辑自定义命令"""
        if 0 <= index < len(self.custom_commands):
            dialog = AddCommandDialog(self, edit_mode=True, command_data=self.custom_commands[index])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                cmd_data = dialog.get_command()
                if cmd_data['name'] and cmd_data['command']:
                    self.custom_commands[index] = cmd_data
                    self.save_custom_commands()
                    self.refresh_custom_commands()
                    QMessageBox.information(self, "成功", f"已更新命令: {cmd_data['name']}")
                else:
                    QMessageBox.warning(self, "错误", "命令名称和内容不能为空！")
    
    def delete_custom_command(self, index):
        """删除自定义命令"""
        if 0 <= index < len(self.custom_commands):
            cmd_name = self.custom_commands[index]['name']
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除命令 '{cmd_name}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.custom_commands.pop(index)
                self.save_custom_commands()
                self.refresh_custom_commands()
    
    def create_command_button(self, name, command):
        btn = QPushButton(name)
        btn.clicked.connect(lambda: self.execute_command(command, name))
        btn.setToolTip(f"执行命令: {command}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def execute_command(self, command, name):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.output_text.append(f"\n{'='*60}")
        self.output_text.append(f"🔧 执行命令: {name}")
        self.output_text.append(f"💻 命令内容: {command}")
        self.output_text.append(f"⏰ 时间: {current_time}")
        self.output_text.append(f"{'='*60}\n")
        
        self.executor = CommandExecutor(command)
        self.executor.output_signal.connect(self.update_output)
        self.executor.finished_signal.connect(self.command_finished)
        self.executor.start()
    
    def update_output(self, text):
        self.output_text.append(text)
        # 自动滚动到底部
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def command_finished(self, success):
        if success:
            self.output_text.append("\n✅ 命令执行完成\n")
        else:
            self.output_text.append("\n⚠️ 命令执行可能存在问题\n")
        
        # 自动滚动到底部
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    app = QApplication(sys.argv)
    window = LetYouHandApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
