"""获取窗口位置测试"""
import win32gui
import win32con

# 枚举所有窗口
def enum_windows():
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and "微信" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append({
                    "hwnd": hwnd,
                    "title": title,
                    "rect": rect,
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                })
        return True

    win32gui.EnumWindows(callback, None)
    return windows

# 获取前台窗口
def get_foreground_window():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    return {
        "hwnd": hwnd,
        "title": title,
        "rect": rect,
        "left": rect[0],
        "top": rect[1],
        "width": rect[2] - rect[0],
        "height": rect[3] - rect[1]
    }

print("=" * 50)
print("获取微信窗口位置")
print("=" * 50)
print()

# 方法1：枚举查找微信
print("[方法1] 枚举查找微信窗口:")
weixin_windows = enum_windows()
if weixin_windows:
    for w in weixin_windows:
        print(f"  标题: {w['title']}")
        print(f"  位置: ({w['left']}, {w['top']})")
        print(f"  大小: {w['width']}x{w['height']}")
        print(f"  完整区域: {w['rect']}")
else:
    print("  未找到微信窗口")

print()

# 方法2：前台窗口
print("[方法2] 当前前台窗口:")
fg = get_foreground_window()
print(f"  标题: {fg['title']}")
print(f"  位置: ({fg['left']}, {fg['top']})")
print(f"  大小: {fg['width']}x{fg['height']}")
print(f"  完整区域: left={fg['left']}, top={fg['top']}, right={fg['rect'][2]}, bottom={fg['rect'][3]}")