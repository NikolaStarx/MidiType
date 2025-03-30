# main.py
# 详细中文注释：该文件为程序入口。主要功能包括：
# - 从配置文件加载参数和映射关系
# - 初始化全局状态 app_state
# - 创建 PyQt 应用窗口
# - 启动后台线程监听 MIDI 消息

import json, threading, mido
from time import sleep
from pynput.keyboard import Controller
from app_state import app_state
from utils.config_loader import load_config
from core.midi_dispatcher import handle_midi
from core.audio_player import get_available_sound_packs, change_sound_pack

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.piano_overlay import PianoOverlay
from gui import piano_overlay_instance
import sys

def midi_listener():
    # 此函数用于监听 MIDI 输入设备，读取并处理每条 MIDI 消息
    try:
        names = mido.get_input_names()  # 获取系统中的 MIDI 设备名称列表
        if not names:
            # 如果未找到 MIDI 设备，则输出错误信息并退出函数
            print("❌ 未找到 MIDI 输入设备")
            return
        print("🎧 正在监听 MIDI 设备: ", names[0])
        with mido.open_input(names[0]) as inport:
            for msg in inport:
                # 对每条 MIDI 消息调用 handle_midi 进行处理
                handle_midi(msg,
                            repeat_enabled=repeat_enabled,
                            repeat_delay=repeat_delay,
                            repeat_rate=repeat_rate)
    except Exception as e:
        print(f"❌ MIDI 错误: {e}")

if __name__ == "__main__":
    # 程序入口：加载配置、初始化状态、启动应用窗口和 MIDI 监听线程
    # 从配置文件加载程序相关参数，如按键重复、主副映射等配置
    # === 加载配置 ===
    config = load_config()
    repeat_delay = config.get("repeat_delay", 0.35)
    repeat_rate = config.get("repeat_rate", 10.0)
    repeat_enabled = config.get("repeat_enabled", True)

    # === 加载映射文件 ===
    with open(config["main_mapping_path"], "r", encoding="utf-8") as f:
        main_mapping = json.load(f)
    with open(config["alt_mapping_path"], "r", encoding="utf-8") as f:
        alt_mapping = json.load(f)

    # === 初始化音色 ===
    # 扫描可用音色包
    sound_packs = get_available_sound_packs()
    if sound_packs:
        # 如果配置中指定了乐器名称，尝试找到对应的音色包
        configured_instrument = config.get("instrument", "")
        selected_pack = None
        
        if isinstance(configured_instrument, str) and configured_instrument:
            # 按名称查找
            for pack in sound_packs:
                if pack['name'].lower() == configured_instrument.lower():
                    selected_pack = pack
                    break
        
        # 如果未找到指定音色或未指定，使用第一个可用音色
        if not selected_pack and sound_packs:
            selected_pack = sound_packs[0]
        
        # 应用选中的音色包
        if selected_pack:
            change_sound_pack(selected_pack['path'])
            print(f"初始化音色: {selected_pack['name']}")
    else:
        print("警告: 未找到可用的音色包")

    # 初始化全局应用状态，将配置参数、键盘控制对象和映射关系保存到 app_state 中
    app_state.update({
        "music_mode": config.get("music_mode", True),
        "instrument": config.get("instrument", 0),
        "pedal_control": config.get("pedal_control", 64),
        "current_mapping_name": "main",
        "main_mapping": main_mapping,
        "alt_mapping": alt_mapping,
        "keyboard": Controller(),
        "repeat_threads": {}
    })

    # 创建 PyQt5 应用对象，并构造程序主窗口
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # 初始化并显示虚拟钢琴键盘overlay的实例
    piano_overlay_instance.piano_overlay = PianoOverlay()
    piano_overlay_instance.piano_overlay.show()

    # 启动一个后台线程，持续监听 MIDI 设备发送的消息
    threading.Thread(target=midi_listener, daemon=True).start()
    print("✅ MIDI 模拟器后台线程已启动（组合键 + 自动连发）")

    # 进入 Qt 事件循环，等待用户与程序界面的交互
    sys.exit(app.exec_())
