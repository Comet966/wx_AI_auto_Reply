"""测试键盘输入 - 中文优化版"""
import pyperclip
import pyautogui as pag
import time
import random

def send_text(text):
    """发送文本 - 中文优化（粘贴+随机延迟防封）"""
    # 随机延迟 1-3 秒，模拟人工操作
    delay = random.uniform(1, 3)
    print(f"  等待 {delay:.1f} 秒...")
    time.sleep(delay)

    # 复制到剪贴板
    original = pyperclip.paste()
    pyperclip.copy(text)
    time.sleep(0.2)

    # 粘贴
    pag.hotkey("ctrl", "v")
    time.sleep(0.3)

    # 发送
    pag.press("enter")
    print(f"  已发送: {text}")

    # 恢复剪贴板
    time.sleep(0.2)
    pyperclip.copy(original)


print("=" * 50)
print("测试键盘输入 - 中文优化版")
print("=" * 50)
print()

# 倒计时
print("请切换到微信窗口，点击聊天框...")
for i in range(5, 0, -1):
    print(f"倒计时 {i} 秒...")
    time.sleep(1)

print()
print("=" * 50)
print("开始测试...")
print("=" * 50)

# 测试1
send_text("测试中文ABC123")

time.sleep(1)

# 测试2
send_text("第二条消息 测试")

time.sleep(1)

# 测试3
send_text("第三条 中文测试OK")

print()
print("=" * 50)
print("✓ 测试完成")
print("共发送3条消息，请检查微信")