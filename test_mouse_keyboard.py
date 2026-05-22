"""Test keyboard and mouse control."""
import time
import pygetwindow as gw
import pyautogui as pag

print("=== 测试键鼠控制 ===\n")

# Test 1: Find WeChat window
print("1. 寻找微信窗口...")
windows = gw.getWindowsWithTitle("微信")
if windows:
    win = windows[0]
    print(f"   ✓ 找到: {win.title}")
    print(f"     位置: ({win.left}, {win.top})")
    print(f"     大小: {win.width}x{win.height}")
else:
    print("   ✗ 未找到微信窗口")
    print("   请确保微信已打开")
    exit(1)

# Bring to front
print("\n2. 激活窗口...")
win.activate()
time.sleep(0.5)
print("   ✓ 已激活")

# Test 2: Mouse click
print("\n3. 测试鼠标点击...")
current_pos = pag.position()
print(f"   当前鼠标位置: {current_pos}")

# Click on a test position (center of window)
test_x = win.left + win.width // 2
test_y = win.top + win.height // 2
print(f"   点击位置: ({test_x}, {test_y})")

pag.click(test_x, test_y)
print("   ✓ 点击完成")

# Test 3: Keyboard input
print("\n4. 测试键盘输入...")
test_text = "测试消息123"
print(f"   输入: {test_text}")

# Use clipboard for reliable Chinese input
import pyperclip
original = pyperclip.paste()
pyperclip.copy(test_text)
time.sleep(0.1)
pag.hotkey("ctrl", "v")
print("   ✓ 输入完成")

# Restore clipboard
pyperclip.copy(original)

# Test 4: Press Enter
print("\n5. 测试回车键...")
pag.press("enter")
print("   ✓ 已发送")

print("\n=== 键鼠测试完成 ===")
print("\n提示: 如果上述操作都在微信窗口中执行，说明键鼠控制正常")