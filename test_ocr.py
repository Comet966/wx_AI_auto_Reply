"""OCR测试脚本"""
import win32gui
import mss
from PIL import Image
from cnocr import CnOcr


def find_wechat():
    """找微信窗口"""
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "微信":
                rect = win32gui.GetWindowRect(hwnd)
                if rect[0] >= 0:
                    windows.append({"left": rect[0], "top": rect[1], "width": rect[2]-rect[0], "height": rect[3]-rect[1]})
        return True
    win32gui.EnumWindows(callback, None)
    return windows[0] if windows else None


def capture_bottom(win):
    """截取下方区域（对方消息）"""
    # 上方40%区域
    left = win["left"] + win["width"] // 4
    top = win["top"] + int(win["height"] * 0.15)
    width = win["width"] * 3 // 4
    height = int(win["height"] * 0.40)

    with mss.MSS() as sct:
        img = sct.grab({"left": left, "top": top, "width": width, "height": height})
        img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
    return img


def main():
    print("=" * 50)
    print("OCR测试")
    print("=" * 50)

    win = find_wechat()
    if not win:
        print("未找到微信")
        return

    print(f"窗口: {win['width']}x{win['height']} ({win['left']},{win['top']})")

    ocr = CnOcr()
    img = capture_bottom(win)

    print("识别中...")
    results = ocr.ocr(img)

    # 过滤
    import re
    time_pat = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
    ui_kw = ["发送", "图片", "表情", "文件", "视频", "语音", "名片", "位置"]

    texts = []
    for r in results:
        if not r or "text" not in r:
            continue
        t = r["text"]
        if t in ui_kw or time_pat.match(t) or len(t) < 2:
            continue
        texts.append(t)

    print()
    print(f"结果 ({len(texts)}条):")
    for i, t in enumerate(texts):
        print(f"  {i+1}. {t}")


if __name__ == "__main__":
    main()