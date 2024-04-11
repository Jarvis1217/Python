"""
1.安装依赖: pip install pynput Pillow
2.运行之后隐藏到后台
3.按"Alt+A"开始截图
"""

from pynput import mouse, keyboard
from PIL import ImageGrab
import os
import sys
import threading

# 全局变量用于存储鼠标按下的位置和释放的位置
start_pos = None
end_pos = None

def on_click(x, y, button, pressed):
    global start_pos, end_pos
    if pressed:
        start_pos = (x, y)
    else:
        end_pos = (x, y)
        # 当鼠标释放时，停止监听鼠标事件
        return False

def take_screenshot():
    global start_pos, end_pos
    # 监听鼠标按下和释放事件来确定截图区域
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    if start_pos and end_pos:
        # 根据选择的区域截图
        screenshot = ImageGrab.grab(bbox=(start_pos[0], start_pos[1], end_pos[0], end_pos[1]))
        # 保存截图
        filepath = os.path.join(sys.path[0], "screenshot.png")
        screenshot.save(filepath)
        print(f"截图已保存到：{filepath}")
    else:
        print("截图失败，请重新尝试。")

def on_activate_screenshot():
    print("开始截图，请选择区域...")
    screenshot_thread = threading.Thread(target=take_screenshot)
    screenshot_thread.start()

# 设置监听快捷键“Alt+A”
hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<alt>+a'),
    on_activate_screenshot
)

def for_canonical(f):
    return lambda k: f(l.canonical(k))

with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()
