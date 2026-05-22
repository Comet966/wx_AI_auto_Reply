"""微信自动回复 - 手动指定区域版本"""
import os
import sys
import time
import pathlib

# 添加项目根目录到路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cnocr import CnOcr
import pyperclip
import pyautogui as pag
import mss
import yaml


class Config:
    """简化配置"""
    def __init__(self):
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


class APIClient:
    """简化API客户端"""
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
        import requests
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
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        # 加入历史
        ctx = self.history[-self.config.context_window:]
        messages.extend(ctx)
        messages.append({"role": "user", "content": user_message})

        response = self.chat(messages)
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})
        return response


class WeChatBot:
    """微信自动回复机器人"""
    def __init__(self):
        self.config = Config()
        self.client = APIClient(self.config)
        self.ocr = CnOcr()
        self.running = False
        self.reply_count = 0

    def capture_region(self, region):
        with mss.MSS() as sct:
            screenshot = sct.grab(region)
            from PIL import Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    def recognize(self, img):
        results = self.ocr.ocr(img)
        texts = [line["text"] for line in results if line and "text" in line]
        return texts

    def generate_reply(self, messages):
        content = "\n".join(messages[-5:])
        reply = self.client.chat_with_context(content)
        return reply

    def send_reply(self, text):
        original = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.1)
        pag.hotkey("ctrl", "v")
        time.sleep(0.2)
        pag.press("enter")
        time.sleep(0.2)
        pyperclip.copy(original)
        self.reply_count += 1
        return True


def test_recognize():
    """测试OCR识别"""
    print("=" * 50)
    print("测试 OCR 识别")
    print("=" * 50)
    print()

    region_str = input("请输入区域坐标 (left,top,width,height): ").strip()
    if not region_str:
        print("使用示例区域: 480,360,960,540")
        region = {"left": 480, "top": 360, "width": 960, "height": 540}
    else:
        left, top, width, height = map(int, region_str.split(","))
        region = {"left": left, "top": top, "width": width, "height": height}

    bot = WeChatBot()
    print(f"\n截取区域: {region}")
    print("识别中...")

    img = bot.capture_region(region)
    texts = bot.recognize(img)

    print()
    print("=" * 40)
    print(f"识别结果 ({len(texts)} 行):")
    print("=" * 40)
    for i, t in enumerate(texts):
        print(f"{i+1}. {t}")


def run_manual():
    """手动模式"""
    print("=" * 50)
    print("微信自动回复 - 手动模式")
    print("=" * 50)
    print()
    print("使用方法:")
    print("1. 在微信中打开目标聊天窗口")
    print("2. 输入消息区域坐标 (left,top,width,height)")
    print()

    region_str = input("请输入区域坐标: ").strip()
    if not region_str:
        region = {"left": 480, "top": 360, "width": 960, "height": 540}
    else:
        left, top, width, height = map(int, region_str.split(","))
        region = {"left": left, "top": top, "width": width, "height": height}

    print(f"区域: ({region['left']}, {region['top']}) {region['width']}x{region['height']}")

    bot = WeChatBot()
    last_texts = []

    print("=" * 50)
    print("开始监控... 按 Ctrl+C 停止")
    print("=" * 50)

    while True:
        try:
            img = bot.capture_region(region)
            texts = bot.recognize(img)

            if texts and texts != last_texts:
                print(f"\n[{time.strftime('%H:%M:%S')}] 新消息:")
                for t in texts[-3:]:
                    print(f"  - {t}")

                reply = bot.generate_reply(texts)
                print(f"[AI] {reply}")

                send = input("\n发送回复? (y/n): ").strip().lower()
                if send == "y":
                    bot.send_reply(reply)
                    print("✓ 已发送")

                last_texts = texts

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
        test_recognize()
    else:
        run_manual()