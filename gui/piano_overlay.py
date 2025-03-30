"""该模块用于实现钢琴键盘的覆盖窗口（PianoOverlay），
用于在屏幕上显示虚拟钢琴键盘，展示当前按下的音符以及映射标签。
它支持多种主题、透明度调节和工具栏控制，由 PyQt5 实现。
"""
import json, os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QToolButton, QFrame, QColorDialog
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont

from app_state import app_state

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# 判断该音符是否为黑键（钢琴上黑色的琴键），返回 True 表示是黑键
def is_black(note):
    return note % 12 in [1, 3, 6, 8, 10]

# 定义特殊符号映射，用于将特定按键名称转换为对应的显示符号
SPECIAL_SYMBOLS = {
    "enter": "↵",
    "return": "↵",
    "backspace": "⇤",
    "space": "▭",
    "capslock": "⇧",
    "shift": "▲"
}

class PianoOverlay(QWidget):
    """该类实现了一个虚拟钢琴键盘覆盖窗口，具备以下功能：
    - 显示从 start_note 到 end_note 的琴键（包括白键和黑键）
    - 高亮显示当前活动的音符
    - 支持切换主副映射，显示不同的标签组合
    - 提供工具栏，用于调节透明度、主题设置及其他操作
    """
    def __init__(self, start_note=48, end_note=84, key_width=40):
        # 构造函数：初始化窗口属性、加载主题、构建标签以及设置工具栏
        super().__init__()
        self.setWindowTitle("虚拟钢琴键盘")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.start_note = start_note
        self.end_note = end_note
        self.key_width = key_width
        self.black_key_width = int(key_width * 0.6)
        self.white_key_height = 160
        self.black_key_height = 100
        self.opacity = 0.92
        self.setWindowOpacity(self.opacity)

        self.active_notes = set()
        self._drag_pos = None
        self.show_labels = True
        self.toolbar_visible = True

        self.load_themes()
        self.current_theme = "normal"

        # 新增：主副映射标注组
        self.labels_main = {}
        self.labels_alt = {}
        self.active_label_group = "main"
        self.build_labels()

        self.toolbar = self.create_toolbar()
        self.toolbar.setParent(self)
        self.toolbar.move(0, 0)
        self.toolbar.show()

        self.resize(self.calculate_width(), self.white_key_height)

    def load_themes(self):
        # 从 JSON 文件中加载主题配置，并初始化默认和自定义主题
        theme_file = os.path.join(os.path.dirname(__file__), "piano_overlay.json")
        with open(theme_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.themes = data["themes"]
        self.themes["custom"] = data["custom"]

    def create_toolbar(self):
        # 创建工具栏，工具栏包含调节透明度、切换标签显示和主题选项的控件
        bar = QFrame()
        bar.setFrameShape(QFrame.StyledPanel)
        bar.setStyleSheet("background-color: rgba(240, 240, 240, 220);")
        bar.setFixedHeight(40)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        toggle_btn = QToolButton()
        toggle_btn.setText("🔽")
        toggle_btn.clicked.connect(self.toggle_toolbar)
        layout.addWidget(toggle_btn)

        layout.addWidget(QLabel("透明度"))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(30, 100)
        slider.setValue(int(self.opacity * 100))
        slider.setFixedWidth(100)
        slider.valueChanged.connect(lambda v: self.set_opacity(v / 100))
        layout.addWidget(slider)

        eye_btn = QPushButton("👁️")
        eye_btn.setCheckable(True)
        eye_btn.setChecked(self.show_labels)
        eye_btn.clicked.connect(self.toggle_labels)
        layout.addWidget(eye_btn)

        for i, name in enumerate(["normal", "dark", "retro"], 1):
            btn = QPushButton(str(i))
            btn.setFixedWidth(28)
            btn.clicked.connect(lambda _, n=name: self.set_theme(n))
            layout.addWidget(btn)

        custom_btn = QPushButton("🎨")
        custom_btn.clicked.connect(self.choose_custom_theme)
        layout.addWidget(custom_btn)

        close_btn = QPushButton("❌")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return bar

    def toggle_toolbar(self):
        # 切换显示或隐藏工具栏
        self.toolbar_visible = not self.toolbar_visible
        self.toolbar.setVisible(self.toolbar_visible)
        self.update()

    def choose_custom_theme(self):
        # 弹出颜色选择对话框，让用户自定义主题颜色，并应用自定义主题
        for key in ["white", "black", "highlight", "toolbar"]:
            color = QColorDialog.getColor()
            if color.isValid():
                self.themes["custom"][key] = color.name()
        self.set_theme("custom")

    def toggle_labels(self):
        # 切换是否在琴键上显示映射标签
        self.show_labels = not self.show_labels
        self.update()

    def set_theme(self, name):
        # 设置当前使用的主题，并刷新界面显示
        self.current_theme = name
        self.update()

    def set_opacity(self, value):
        # 设置窗口透明度
        self.opacity = value
        self.setWindowOpacity(value)

    def calculate_width(self):
        # 根据定义的起始和结束音符（仅计白键）来计算窗口宽度
        return len([n for n in range(self.start_note, self.end_note + 1) if not is_black(n)]) * self.key_width

    def build_labels(self):
        # 生成琴键上的映射标签，基于 app_state 中的主映射和备用映射数据
        main_map = app_state.get("main_mapping", {})
        alt_map = app_state.get("alt_mapping", {})
        for note in range(self.start_note, self.end_note + 1):
            m = main_map.get(str(note), "")
            a = alt_map.get(str(note), "")
            self.labels_main[note] = SPECIAL_SYMBOLS.get(m.lower(), m)
            self.labels_alt[note] = SPECIAL_SYMBOLS.get(a.lower(), a)

    def set_label_group(self, group):
        # 设置当前显示的标签组（'main' 或 'alt'），并刷新界面
        if group in ["main", "alt"]:
            self.active_label_group = group
            self.update()

    def note_on(self, note):
        # 当音符按下时，记录该音符并刷新界面以高亮显示对应琴键
        print(f"🎹 note_on 被调用，音符: {note}")
        self.active_notes.add(note)
        self.update()

    def note_off(self, note):
        # 当音符释放时，移除高亮显示并刷新界面
        print(f"🎹 note_off 被调用，音符: {note}")
        self.active_notes.discard(note)
        self.update()

    def mousePressEvent(self, event):
        # 鼠标按下事件：记录鼠标位置，用于实现窗口拖动
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        # 鼠标移动事件：如果处于拖动状态，则更新窗口位置
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        # 鼠标释放事件：当工具栏隐藏且点击左上角特定区域时，显示工具栏
        if not self.toolbar_visible and event.pos().x() <= 30 and event.pos().y() <= 20:
            self.toggle_toolbar()

    def paintEvent(self, event):
        # 重绘窗口：根据当前状态绘制白键、黑键及映射标签，展现按键高亮效果
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        theme = self.themes[self.current_theme]

        white_notes = []
        black_notes = []
        for n in range(self.start_note, self.end_note + 1):
            (black_notes if is_black(n) else white_notes).append(n)

        note_to_x = {}
        x = 0
        for n in white_notes:
            note_to_x[n] = x
            color = QColor(theme["highlight"]) if n in self.active_notes else QColor(theme["white"])
            painter.setBrush(color)
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(x, 0, self.key_width, self.white_key_height)

            if self.show_labels:
                label = self.labels_main[n] if self.active_label_group == "main" else self.labels_alt[n]
                painter.setPen(QColor(0, 0, 0))
                font = QFont("Arial", 10)
                painter.setFont(font)
                painter.drawText(x + 6, int(self.white_key_height * 0.8), label)

            x += self.key_width

        for n in black_notes:
            prev_white = n - 1
            if prev_white in note_to_x:
                x = note_to_x[prev_white] + self.key_width - self.black_key_width // 2
                color = QColor(theme["highlight"]) if n in self.active_notes else QColor(theme["black"])
                painter.setBrush(color)
                painter.setPen(Qt.NoPen)
                painter.drawRect(x, 0, self.black_key_width, self.black_key_height)

                if self.show_labels:
                    label = self.labels_main[n] if self.active_label_group == "main" else self.labels_alt[n]
                    painter.setPen(QColor(255, 255, 255))
                    font = QFont("Arial", 9)
                    painter.setFont(font)
                    painter.drawText(x + 3, int(self.black_key_height / 2 + 5), label)

        if not self.toolbar_visible:
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(6, 16, "🔼")
