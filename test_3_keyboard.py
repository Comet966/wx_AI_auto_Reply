"""测试 3: 键盘输入"""
import pyperclip
import pyautogui as pag
import time

print("=" * 50)
print("测试 键盘输入")
print("=" * 50)
print()
print("[说明] 请在微信聊天框中点击一下，")
print("       然后程序会自动输入测试文本并按回车发送")
print()
input("准备完成后按回车开始...")

print()

# 测试文本
test_text = "测试消息: 你好，这是自动发送的测试"

print(f"[1] 复制到剪贴板: {test_text}")

# 保存原剪贴板内容
original = pyperclip.paste()

# 复制新内容
pyperclip.copy(test_text)
time.sleep(0.2)

print("[2] 粘贴 (Ctrl+V)...")
pag.hotkey("ctrl", "v")
time.sleep(0.3)

print("[3] 按回车发送...")
pag.press("enter")

# 恢复剪贴板
time.sleep(0.2)
pyperclip.copy(original)

print()
print("=" * 50)
print("✓ 键盘输入测试完成")
print()
print("请查看微信是否收到了这条消息")