# core/midi_dispatcher.py
"""
该模块用于处理接收到的 MIDI 消息，
根据消息类型进行不同的操作：
- 控制变化消息: 切换踏板映射组并更新 piano_overlay 显示
- note_on 消息: 模拟键盘按下事件，启动重复按键线程（如启用），并通知 piano_overlay 高亮显示音符
- note_off 消息: 模拟键盘释放，停止重复按键线程，并通知 piano_overlay 取消高亮
"""

from app_state import app_state
from utils.keycode_utils import get_key_obj, is_repeatable
from core.repeater import start_repeat_thread, stop_repeat_thread

# ✅ 引入共享 piano_overlay 实例
# from gui.piano_overlay_instance import piano_overlay

# 替换为：
import gui.piano_overlay_instance

# 添加音频播放器导入（尝试导入，如果出错则忽略，以便在没有pygame的环境中也能运行）
try:
    from core.audio_player import play_sound
except ImportError:
    # 定义一个空函数，确保在没有音频模块时程序仍然可以运行
    def play_sound(note):
        print(f"音频模块未加载，无法播放音符 {note}")

note_to_key = {}

def handle_midi(msg, repeat_enabled=True, repeat_delay=0.35, repeat_rate=10.0):
    # 处理踏板控制：当收到 control_change 消息且控制号匹配时，根据踏板输入值切换映射组
    if msg.type == 'control_change' and msg.control == app_state["pedal_control"]:
        # ✅ 踏板切换主/副映射
        group = "alt" if msg.value >= 64 else "main"
        app_state["current_mapping_name"] = group
        print(f"🎮 踏板切换映射组 → {group}")

        # ✅ 通知 piano_overlay 显示对应映射标注
        if gui.piano_overlay_instance.piano_overlay:
            print(f"🔁 调用 piano_overlay.set_label_group('{group}')")
            gui.piano_overlay_instance.piano_overlay.set_label_group(group)

    # 处理按键按下：当收到 note_on 消息且 velocity 大于 0 时，查找当前映射中的对应键名，模拟键盘按下，并启动重复按键线程（若启用）
    elif msg.type == 'note_on' and msg.velocity > 0:
        mapping = app_state["main_mapping"] if app_state["current_mapping_name"] == "main" else app_state["alt_mapping"]
        note = str(msg.note)
        if note in mapping:
            keyname = mapping[note]
            key = get_key_obj(keyname)
            try:
                app_state["keyboard"].press(key)
                note_to_key[note] = key
                print(f"🔽 按下: {keyname}")
                if repeat_enabled and is_repeatable(keyname):
                    start_repeat_thread(note, keyname, key, delay=repeat_delay, rate=repeat_rate)
            except Exception as e:
                print(f"⚠️ 按键错误 {keyname} → {e}")
        else:
            print(f"🎵 无映射: MIDI Note {note}")

        # ✅ 如果音乐模式开启，播放对应的音符声音
        if app_state.get("music_mode", True):
            try:
                play_sound(msg.note)  # 使用MIDI音符号码播放声音
            except Exception as e:
                print(f"⚠️ 播放音效失败: {e}")

        # ✅ 通知 piano_overlay 高亮该音符
        if gui.piano_overlay_instance.piano_overlay:
            print(f"🔔 调用 piano_overlay.note_on({msg.note})")
            gui.piano_overlay_instance.piano_overlay.note_on(msg.note)
        else:
            print("⚠️ piano_overlay 实例未设置")

    # 处理按键释放：当收到 note_off 消息或 note_on (velocity==0) 消息时，释放对应键位，终止重复按键，并通知 piano_overlay 取消高亮
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        note = str(msg.note)
        if note in note_to_key:
            key = note_to_key[note]
            try:
                app_state["keyboard"].release(key)
                print(f"🔾 松开: {key}")
                stop_repeat_thread(note)
            except Exception as e:
                print(f"⚠️ 释放错误 {key}: {e}")
            del note_to_key[note]

        # ✅ 通知 piano_overlay 取消高亮该音符
        if gui.piano_overlay_instance.piano_overlay:
            print(f"🔕 调用 piano_overlay.note_off({msg.note})")
            gui.piano_overlay_instance.piano_overlay.note_off(msg.note)
        else:
            print("⚠️ piano_overlay 实例未设置")
