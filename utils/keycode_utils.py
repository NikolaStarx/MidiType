# utils/keycode_utils.py

from pynput.keyboard import Key

# 特殊键映射表
SPECIAL_KEYS = {
    "enter": Key.enter,
    "return": Key.enter,
    "space": Key.space,
    "shift": Key.shift,
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "tab": Key.tab,
    "capslock": Key.caps_lock,
    "esc": Key.esc,
    "backspace": Key.backspace,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "win": Key.cmd
}

# 支持自动重复输入的键（可连发）
REPEATABLE_KEYS = set(
    list("abcdefghijklmnopqrstuvwxyz0123456789") +
    ["space", "backspace", "=", "-", ",", ".", "/", "\\", ";", "'", "[", "]", 
     "up", "down", "left", "right"]
)

def get_key_obj(keyname: str):
    """将字符串键名映射为 pynput 可识别的 Key 对象或字符"""
    return SPECIAL_KEYS.get(keyname.lower(), keyname.lower())

def is_repeatable(keyname: str) -> bool:
    """判断该键是否支持自动重复输入"""
    return keyname.lower() in REPEATABLE_KEYS
