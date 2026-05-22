"""微信自动回复 - 精确窗口定位版本"""
import os
import sys
import pathlib
import time
import random
import win32gui
import win32con

project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cnocr import CnOcr
import pyperclip
import pyautogui as pag
import mss
import yaml


class Config:
    def __init__(self):
        config_path = project_root / "config.yaml"
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.api_key = data["api"]["key"]
        self.model = data["api"]["model"]
        self.base_url = data["api"]["base_url"]
        self.system_prompt = data["ai"].get("system_prompt", "")
        self.max_daily = data["safety"].get("max_daily", 200)


def find_wechat_window():
    """找到微信窗口"""
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "微信":  # 精确匹配
                rect = win32gui.GetWindowRect(hwnd)
                if rect[0] > 0:  # 只取有效位置的窗口
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2],
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1]
                    })
        return True

    win32gui.EnumWindows(callback, None)
    return windows[0] if windows else None


class APIClient:
    def __init__(self, config):
        import requests
        self.config = config
        self.session = requests.Session()
        self.session.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        self.history = []

    def chat(self, messages):
        url = f"{self.config.base_url}/chat/completions"
        payload = {"model": self.config.model, "messages": messages}
        resp = self.session.post(url, json=payload, timeout=30)
        return resp.json()["choices"][0]["message"]["content"]

    def chat_with_context(self, user_message):
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.extend(self.history[-10:])
        messages.append({"role": "user", "content": user_message})
        response = self.chat(messages)
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})
        return response


class WeChatBot:
    def __init__(self):
        self.config = Config()
        self.client = APIClient(self.config)
        self.ocr = CnOcr()
        self.reply_count = 0
        self.last_texts = []
        self.daily_count = 0
        self.window = None

    def find_window(self):
        """查找微信窗口"""
        self.window = find_wechat_window()
        if self.window:
            print(f"✓ 找到微信窗口: ({self.window['left']}, {self.window['top']}) {self.window['width']}x{self.window['height']}")
            return True
        print("❌ 未找到微信窗口")
        return False

    def capture_right_half(self):
        """截取微信窗口右半边（去掉联系人列表）"""
        if not self.window:
            return None, None

        # 微信窗口左边的1/4是联系人列表，右边3/4是聊天区域
        left = self.window["left"] + self.window["width"] // 4
        top = self.window["top"]
        width = self.window["width"] * 3 // 4
        height = self.window["height"]

        region = {"left": left, "top": top, "width": width, "height": height}

        with mss.MSS() as sct:
            screenshot = sct.grab(region)
            from PIL import Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        return img, region

    def recognize(self, img):
        results = self.ocr.ocr(img)
        texts = [line["text"] for line in results if line and "text" in line]
        return texts

    def generate_reply(self, messages):
        content = "\n".join(messages[-5:])
        return self.client.chat_with_context(content)

    def send_reply(self, text):
        """发送回复 - 带防封随机延迟"""
        time.sleep(random.uniform(1, 3))

        original = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.1)

        pag.hotkey("ctrl", "v")
        time.sleep(random.uniform(0.2, 0.5))
        pag.press("enter")
        time.sleep(0.2)
        pyperclip.copy(original)

        self.reply_count += 1
        self.daily_count += 1


def test():
    """测试：截取微信窗口右半边识别"""
    print("=" * 50)
    print("测试：截取微信窗口右半边识别")
    print("=" * 50)
    print()

    bot = WeChatBot()
    if not bot.find_window():
        return

    print()
    img, region = bot.capture_right_half()
    if not img:
        print("❌ 无法截取")
        return

    print(f"区域: ({region['left']}, {region['top']}) {region['width']}x{region['height']}")
    print(f"尺寸: {img.size}")
    print()
    print("识别中...")

    texts = bot.recognize(img)

    print()
    print("=" * 40)
    print(f"识别结果 ({len(texts)} 行):")
    print("=" * 40)
    for i, t in enumerate(texts[:25]):
        print(f"{i+1}. {t}")


def run():
    """运行自动回复"""
    print("=" * 50)
    print("微信自动回复 - 自动模式")
    print("=" * 50)
    print()

    bot = WeChatBot()
    if not bot.find_window():
        return

    print()
    print("=" * 50)
    print("开始监控... 按 Ctrl+C 停止")
    print("=" * 50)

    while True:
        try:
            img, region = bot.capture_right_half()
            if not img:
                time.sleep(1)
                continue

            texts = bot.recognize(img)

            if texts and texts != bot.last_texts:
                new_msgs = texts[-5:] if len(texts) >= 5 else texts
                print(f"\n[{time.strftime('%H:%M:%S')}] 新消息:")
                for t in new_msgs:
                    print(f"  - {t}")

                reply = bot.generate_reply(texts)
                print(f"[AI] {reply}")

                send = input("\n发送回复? (y/n): ").strip().lower()
                if send == "y":
                    bot.send_reply(reply)
                    print("✓ 已发送")

                bot.last_texts = texts

            time.sleep(3)

        except KeyboardInterrupt:
            break

    print(f"\n总回复数: {bot.reply_count}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", choices=["run", "test"])
    args = parser.parse_args()

    if args.mode == "test":
        test()
    else:
        run()