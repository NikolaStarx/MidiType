# 文件: gui/piano_overlay_instance.py
"""
该文件用于存储全局的 piano_overlay 实例。
其他模块可以从此处导入 piano_overlay，
以便在需要时共享同一个虚拟钢琴覆盖窗口实例。
"""

piano_overlay = None  # 全局变量，保存 PianoOverlay 实例（初始值为 None）
