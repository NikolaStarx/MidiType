# gui/main_window.py

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QSystemTrayIcon, QMenu, QAction, QMessageBox, QCheckBox, QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import os
from app_state import app_state

from gui.piano_overlay import PianoOverlay
# from gui.mapping_editor import MappingEditor
from gui import piano_overlay_instance # Import the global instance file

# 导入音频播放器相关功能
from core.audio_player import get_available_sound_packs, change_sound_pack

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDIType 控制中心")
        self.setGeometry(200, 200, 400, 300)

        # 中央组件布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 按钮：显示/隐藏钢琴
        self.piano_overlay = PianoOverlay()
        piano_overlay_instance.piano_overlay = self.piano_overlay  # Ensure global instance is set
        print("✅ 主窗口创建并注册了 piano_overlay 实例", self.piano_overlay)

        self.btn_toggle_piano = QPushButton("🎹 显示虚拟钢琴键盘")
        self.btn_toggle_piano.clicked.connect(self.toggle_piano_overlay)
        self.layout.addWidget(self.btn_toggle_piano)

        # 按钮：打开映射编辑器
        self.btn_open_editor = QPushButton("🛠 打开映射编辑器")
        self.btn_open_editor.clicked.connect(self.open_mapping_editor)
        self.layout.addWidget(self.btn_open_editor)

        # 新增：音乐模式开关和音色选择器
        # 音乐模式开关：勾选时开启音乐模式，否则关闭
        self.music_mode_checkbox = QCheckBox("开启音乐模式")
        # 从全局状态 app_state 获取默认值，若未设置，默认开启
        self.music_mode_checkbox.setChecked(app_state.get("music_mode", True))
        self.music_mode_checkbox.toggled.connect(self.toggle_music_mode)
        self.layout.addWidget(self.music_mode_checkbox)

        # 音色选择器：下拉菜单，用于选择音色
        # 使用动态扫描方式获取可用音色
        self.instrument_select = QComboBox()
        self.sound_packs = get_available_sound_packs()
        
        # 检查是否有可用的音色包
        if self.sound_packs:
            # 添加所有可用的音色到下拉菜单
            for pack in self.sound_packs:
                self.instrument_select.addItem(pack['name'])
            
            # 设置选中项并连接信号
            self.instrument_select.currentIndexChanged.connect(self.change_instrument)
            self.layout.addWidget(self.instrument_select)
        else:
            # 如果没有找到音色包，显示提示信息
            self.no_sounds_label = QCheckBox("未检测到可用音色包")
            self.no_sounds_label.setEnabled(False)
            self.layout.addWidget(self.no_sounds_label)

        # 托盘图标
        tray_icon_path = os.path.join("assets", "icons", "app_icon.png")
        self.tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), self)
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_piano_overlay(self):
        if self.piano_overlay.isVisible():
            self.piano_overlay.hide()
            self.btn_toggle_piano.setText("🎹 显示虚拟钢琴键盘")
        else:
            self.piano_overlay.show()
            self.btn_toggle_piano.setText("🎹 隐藏虚拟钢琴键盘")

    def toggle_music_mode(self, checked):
        # 更新全局状态中的音乐模式标志
        app_state["music_mode"] = checked
        print(f"音乐模式 {'开启' if checked else '关闭'}")

    def change_instrument(self, index):
        # 获取选择的音色包信息
        if not self.sound_packs or index < 0 or index >= len(self.sound_packs):
            return
            
        selected_pack = self.sound_packs[index]
        instrument_name = selected_pack['name']
        sound_path = selected_pack['path']
        
        # 更新全局状态
        app_state["instrument"] = instrument_name
        
        # 切换音色包并加载新音频
        if change_sound_pack(sound_path):
            print(f"已切换音色: {instrument_name}")
        else:
            print(f"切换音色失败: {instrument_name}")

    def open_mapping_editor(self):
        QMessageBox.information(self, "提示", "这里将打开映射编辑器（待实现）")

    def closeEvent(self, event):
        # 最小化到托盘
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "MIDIType 最小化",
            "程序已隐藏至系统托盘，可右键图标退出。",
            QSystemTrayIcon.Information,
            3000
        )

# 入口测试用
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
