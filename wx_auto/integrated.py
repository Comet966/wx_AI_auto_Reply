"""整合测试 - 区域选择 + OCR + API + 发送"""
import json
import time
import os

# 添加项目根目录
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from wx_auto._region_selector import RegionSelector
from wx_auto.screen_capture import ScreenCapture
from wx_auto.wechat_ocr import WeChatOCR
import pyperclip
import pyautogui as pag
import yaml


def load_config():
    """加载配置"""
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_region():
    """加载选区"""
    region_file = os.path.join(project_root, "wx_auto", "selection_result.json")
    if os.path.exists(region_file):
        with open(region_file, encoding="utf-8") as f:
            return json.load(f)
    return None


def select_region():
    """选择区域"""
    print("="*50)
    print("步骤1: 选择微信聊天区域")
    print("="*50)
    print("请拖拽选择要识别的区域（包含对话内容）")
    selector = RegionSelector()
    selector.run()


def recognize_and_reply():
    """识别并回复"""
    print("="*50)
    print("步骤2: OCR识别 + API回复")
    print("="*50)

    # 加载配置
    config = load_config()

    # 加载选区
    region = load_region()
    if not region:
        print("未找到选区，请先运行选择区域")
        return

    print(f"使用区域: {region}")

    # 截图
    cap = ScreenCapture()
    result = cap.capture_region(
        region["x"], region["y"],
        region["width"], region["height"]
    )

    if not result["success"]:
        print(f"截图失败: {result.get('error')}")
        return

    # OCR识别
    ocr = WeChatOCR()
    ocr_result = ocr.recognize(result["image_data"])

    if not ocr_result["success"]:
        print(f"OCR失败: {ocr_result.get('error')}")
        return

    print("\n识别结果:")
    messages = ocr_result.get("messages", [])
    if not messages:
        print("  (无内容)")
        return

    for i, m in enumerate(messages[-3:]):  # 最近3条
        print(f"  {m['speaker']}: {m['content'][:50]}")

    # 取最新一条对方消息
    latest = None
    for m in reversed(messages):
        if m["speaker"] != "我":
            latest = m["content"]
            break

    if not latest:
        print("无对方消息")
        return

    print(f"\n最新消息: {latest}")

    # API调用 - 简化版
    import requests
    api_key = config["api"]["key"]
    model = config["api"]["model"]
    base_url = config["api"]["base_url"]

    system_prompt = config["ai"].get("system_prompt", "你是客服")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": latest}
    ]

    resp = requests.post(
        f"{base_url}/chat/completions",
        json={"model": model, "messages": messages},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30
    )

    reply = resp.json()["choices"][0]["message"]["content"]
    print(f"\nAI回复: {reply}")

    # 发送
    send = input("\n发送回复? (y/n): ").strip().lower()
    if send == "y":
        # 随机延迟
        time.sleep(1.5)

        original = pyperclip.paste()
        pyperclip.copy(reply)
        time.sleep(0.2)
        pag.hotkey("ctrl", "v")
        time.sleep(0.3)
        pag.press("enter")

        print("✓ 已发送")


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["select", "run"])
    args = parser.parse_args()

    if args.action == "select":
        select_region()
    else:
        recognize_and_reply()


if __name__ == "__main__":
    main()