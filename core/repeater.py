# core/repeater.py

import threading
import time
from app_state import app_state
from utils.keycode_utils import is_repeatable

# 启动自动连发线程（需在 MIDI note 按下后调用）
def start_repeat_thread(note, keyname, key_obj, delay=0.35, rate=10.0):
    if not is_repeatable(keyname):
        return

    def repeater():
        time.sleep(delay)
        interval = 1.0 / rate
        while note in app_state["repeat_threads"]:
            app_state["keyboard"].press(key_obj)
            app_state["keyboard"].release(key_obj)
            time.sleep(interval)

    t = threading.Thread(target=repeater, daemon=True)
    app_state["repeat_threads"][note] = t
    t.start()

# 停止对应 MIDI note 的连发线程
def stop_repeat_thread(note):
    if note in app_state["repeat_threads"]:
        del app_state["repeat_threads"][note]
