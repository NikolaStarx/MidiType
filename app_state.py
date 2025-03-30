# app_state.py
# 全局运行状态共享字典

from pynput.keyboard import Controller

app_state = {
    "main_mapping": {},            # 主映射字典（从 mapping1.json 加载）
    "alt_mapping": {},             # 副映射字典（从 mapping2.json 加载）
    "current_mapping_name": "main",# 当前激活映射名："main" or "alt"

    "music_mode": True,            # 是否开启打字发音模式（预留）
    "instrument": 0,               # 当前音色编号（用于发声）
    "pedal_control": 64,           # Control Change 的控制器编号（默认64）

    "keyboard": Controller(),      # 键盘控制器（用于模拟按键）
}


