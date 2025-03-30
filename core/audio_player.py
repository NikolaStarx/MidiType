import os
import pygame
from pprint import pprint

# 初始化 pygame 的 mixer 模块
pygame.mixer.init()

# 全局音频缓存
AUDIO_CACHE = {}

# 音频文件所在目录
SOUNDS_DIR = os.path.join("assets", "sounds", "piano_music")

# MIDI 音符号码 到 音符名称的映射
# 以 C4 为中央 C (MIDI 号码 60)
# 完整的音符列表: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def get_available_sound_packs():
    """返回可用的音色包列表"""
    sounds_dir = os.path.join("assets", "sounds")
    if not os.path.exists(sounds_dir):
        return []
    
    packs = []
    for dirname in os.listdir(sounds_dir):
        full_path = os.path.join(sounds_dir, dirname)
        if os.path.isdir(full_path):
            # 只添加包含有效音频文件的目录
            has_wav_files = any(f.endswith('.wav') for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f)))
            if has_wav_files:
                # 提取乐器名称 (例如 piano_music -> Piano)
                instrument_name = dirname.split('_')[0].capitalize() if '_' in dirname else dirname.capitalize()
                packs.append({
                    'name': instrument_name,
                    'path': full_path
                })
    
    return packs

def change_sound_pack(sound_pack_path):
    """更改当前使用的音色包目录并重新加载音频文件"""
    global SOUNDS_DIR, AUDIO_CACHE
    
    if not os.path.exists(sound_pack_path):
        print(f"音色包路径不存在: {sound_pack_path}")
        return False
    
    # 更新音频目录路径
    SOUNDS_DIR = sound_pack_path
    
    # 清空当前缓存
    AUDIO_CACHE = {}
    
    # 重新加载音频文件
    load_sounds()
    
    return True

def midi_to_note_name(midi_number):
    """将MIDI音符号码转换为音符名称，如60 -> C4"""
    octave = (midi_number // 12) - 1  # MIDI标准中，60为中央C (C4)
    note_idx = midi_number % 12
    return f"{NOTE_NAMES[note_idx]}{octave}"

def note_name_to_filename(note_name, instrument="Piano"):
    """将音符名称转换为音频文件名，如C4 -> Piano_C4.wav"""
    return f"{instrument}_{note_name}.wav"

def load_sounds():
    """加载音频文件到缓存"""
    global AUDIO_CACHE
    
    # 创建MIDI号码到文件路径的映射
    note_file_map = {}
    for filename in os.listdir(SOUNDS_DIR):
        if filename.endswith(".wav"):
            # 假设文件名格式为：Piano_C#1.wav，Piano_D3.wav 等
            try:
                # 从文件名中提取音符名称，如 C#1
                parts = os.path.splitext(filename)[0].split('_')
                if len(parts) >= 2:
                    instrument, note_name = parts[0], parts[1]
                    
                    # 尝试找到所有可能匹配的MIDI号码
                    # 这里我们简单遍历MIDI范围21-108的音符（88键钢琴）
                    for midi_num in range(21, 109):
                        if midi_to_note_name(midi_num) == note_name:
                            note_file_map[midi_num] = os.path.join(SOUNDS_DIR, filename)
                            break
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
    
    # 加载找到的音频文件
    for midi_num, filepath in note_file_map.items():
        try:
            AUDIO_CACHE[midi_num] = pygame.mixer.Sound(filepath)
        except Exception as e:
            print(f"加载音频文件 {filepath} 失败: {e}")
    
    print(f"音频文件加载完成，共加载了 {len(AUDIO_CACHE)} 个音频文件")
    # 打印加载的MIDI号码范围，帮助调试
    if AUDIO_CACHE:
        print(f"已加载MIDI号码范围: {min(AUDIO_CACHE.keys())} 到 {max(AUDIO_CACHE.keys())}")

def play_sound(note):
    """播放指定MIDI号码的音符"""
    sound = AUDIO_CACHE.get(note)
    if sound:
        sound.play()
    else:
        note_name = midi_to_note_name(note)
        print(f"未找到MIDI音符 {note} ({note_name}) 对应的音频文件")

# 初始化时加载音频文件
load_sounds()

# 调试信息：打印部分映射关系
print("MIDI音符到音符名称示例:")
for i in range(60, 73):  # 从中央C (C4) 到 C5
    print(f"MIDI {i} -> {midi_to_note_name(i)}")
