# config_loader.py

import json
import os
from app_state import app_state

DEFAULT_CONFIG = {
    "main_mapping_path": "mappings/mapping1.json",
    "alt_mapping_path": "mappings/mapping2.json",
    "music_mode": True,
    "instrument": 0,
    "pedal_control": 64
}

def load_config(filepath="config.json"):
    if not os.path.exists(filepath):
        print("⚠️ config.json 未找到，使用默认配置")
        config = DEFAULT_CONFIG
        save_config(filepath, config)
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ 配置文件读取失败：{e}")
            config = DEFAULT_CONFIG

    # 同步 app_state
    app_state["music_mode"] = config.get("music_mode", True)
    app_state["instrument"] = config.get("instrument", 0)
    app_state["pedal_control"] = config.get("pedal_control", 64)

    return config  # ✅ 一定要有这一句！

def save_config(filepath="config.json", config_dict=None):
    ...
