"""微信自动回复 - 整合版"""
import pathlib
import time
import random

# 项目根目录
project_root = pathlib.Path(__file__).parent.parent

import sys
sys.path.insert(0, str(project_root))

import win32gui
import mss
import yaml
import requests
import pyperclip
import pyautogui as pag
from cnocr import CnOcr


# ========== 配置模块 ==========
class Config:
    """配置管理"""
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = project_root / "config.yaml"

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.api_key = data["api"]["key"]
        self.model = data["api"]["model"]
        self.base_url = data["api"]["base_url"]
        self.temperature = data["api"].get("temperature", 0.7)
        self.max_tokens = data["api"].get("max_tokens", 500)
        self.system_prompt = data["ai"].get("system_prompt", "")
        self.context_window = data["ai"].get("context_window", 5)

        self.check_interval = data["interval"].get("check", 3)
        self.reply_min = data["interval"].get("reply_min", 2)
        self.reply_max = data["interval"].get("reply_max", 5)

        self.max_daily = data["safety"].get("max_daily", 200)
        self.night_start = data["safety"].get("night_mode_start", 23)
        self.night_end = data["safety"].get("night_mode_end", 8)

        # 运行模式
        self.auto_send = data.get("mode", {}).get("auto_send", False)


# ========== API模块 ==========
class APIClient:
    """DeepSeek API 客户端"""
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        self.history = []  # 对话历史

    def chat(self, messages):
        """发送聊天请求"""
        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def chat_with_context(self, user_message):
        """带上下文的聊天"""
        messages = []

        # system prompt
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        # 历史记录
        ctx = self.history[-self.config.context_window * 2:]
        messages.extend(ctx)

        # 当前消息
        messages.append({"role": "user", "content": user_message})

        # API调用
        response = self.chat(messages)

        # 保存历史
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})

        return response

    def clear_history(self):
        """清空历史"""
        self.history = []


# ========== OCR模块 ==========
class OCRReader:
    """OCR文字识别"""
    def __init__(self):
        print("[OCR] 初始化...")
        self.ocr = CnOcr()
        print("[OCR] 就绪")

    def recognize(self, img):
        """识别图片中的文字"""
        results = self.ocr.ocr(img)
        texts = [line["text"] for line in results if line and "text" in line]
        return texts


# ========== 窗口模块 ==========
class WindowFinder:
    """微信窗口定位"""
    def __init__(self):
        self.window = None

    def find(self):
        """查找微信窗口"""
        windows = []

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title == "微信":
                    rect = win32gui.GetWindowRect(hwnd)
                    if rect[0] >= 0:  # 有效位置（非负）
                        windows.append({
                            "left": rect[0],
                            "top": rect[1],
                            "right": rect[2],
                            "bottom": rect[3],
                            "width": rect[2] - rect[0],
                            "height": rect[3] - rect[1]
                        })
            return True

        win32gui.EnumWindows(callback, None)

        if windows:
            self.window = windows[0]
            return True
        return False

    def capture_chat_area(self):
        """截取消息区域 - 只取上方（对方的消息区域）"""
        if not self.window:
            return None

        # 只取上半部分，约40%（灰色背景是对方的，在上方）
        left = self.window["left"] + self.window["width"] // 4
        top = self.window["top"] + int(self.window["height"] * 0.15)  # 从15%开始
        width = self.window["width"] * 3 // 4
        height = int(self.window["height"] * 0.40)  # 取到55%处

        region = {"left": left, "top": top, "width": width, "height": height}

        region = {"left": left, "top": top, "width": width, "height": height}

        with mss.MSS() as sct:
            screenshot = sct.grab(region)
            from PIL import Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        return img


# ========== 输入模块 ==========
class InputSender:
    """键盘输入发送"""
    def __init__(self):
        self.reply_count = 0

    def send(self, text, delay_range=(1, 3)):
        """发送文本 - 带随机延迟防封"""
        # 随机延迟
        delay = random.uniform(*delay_range)
        time.sleep(delay)

        # 保存剪贴板
        original = pyperclip.paste()

        # 复制内容
        pyperclip.copy(text)
        time.sleep(0.2)

        # 粘贴
        pag.hotkey("ctrl", "v")
        time.sleep(0.3)

        # 发送
        pag.press("enter")
        time.sleep(0.2)

        # 恢复剪贴板
        pyperclip.copy(original)

        self.reply_count += 1
        return True


# ========== 主程序 ==========
class WeChatBot:
    """微信自动回复机器人"""
    def __init__(self):
        self.config = Config()
        self.client = APIClient(self.config)
        self.reader = OCRReader()
        self.finder = WindowFinder()
        self.sender = InputSender()

        self.last_texts = []
        self.running = False

    def start(self):
        """启动"""
        print("=" * 50)
        print("微信自动回复助手")
        print("=" * 50)

        # 找窗口
        if not self.finder.find():
            print("❌ 未找到微信窗口")
            return False

        w = self.finder.window
        print(f"✓ 找到微信窗口: {w['width']}x{w['height']} ({w['left']}, {w['top']})")

        self.running = True
        print("\n开始监控... 按 Ctrl+C 停止\n")
        return True

    def run_once(self):
        """运行一次检测"""
        if not self.running:
            return

        # 截图
        img = self.finder.capture_chat_area()
        if not img:
            return

        # OCR识别
        texts = self.reader.recognize(img)

        # 过滤无关内容
        ui_keywords = ["发送", "图片", "表情", "文件", "视频", "语音", "名片", "位置"]
        # 过滤时间戳格式 HH:MM 或 HH:MM:SS
        import re
        time_pattern = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")

        filtered = []
        for t in texts:
            # 排除UI关键字、时间戳、单字
            if t in ui_keywords:
                continue
            if time_pattern.match(t):
                continue
            if len(t) < 2:
                continue
            filtered.append(t)

        # 只取最近1条
        latest_msg = filtered[-1] if filtered else ""

        if latest_msg and latest_msg != self.last_texts:
            print(f"\n[{time.strftime('%H:%M:%S')}] === 新消息 ===")
            print(f"  {latest_msg}")

            reply = self.client.chat_with_context(latest_msg)
            print(f"[AI] {reply}")

            # 根据配置决定是否自动发送
            if self.config.auto_send:
                self.sender.send(reply)
                print("✓ 已自动发送")
            else:
                send = input("\n发送回复? (y/n): ").strip().lower()
                if send == "y":
                    self.sender.send(reply)
                    print("✓ 已发送")

            self.last_texts = texts

    def stop(self):
        """停止"""
        self.running = False
        print(f"\n总回复数: {self.sender.reply_count}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", choices=["run", "test"])
    args = parser.parse_args()

    # 创建机器人
    bot = WeChatBot()
    if not bot.start():
        return

    if bot.config.auto_send:
        print(">>> 自动发送模式 <<<\n")

    if args.mode == "test":
        bot.run_once()
        return

    # 运行
    try:
        while bot.running:
            bot.run_once()
            time.sleep(bot.config.check_interval)
    except KeyboardInterrupt:
        pass

    bot.stop()


if __name__ == "__main__":
    main()