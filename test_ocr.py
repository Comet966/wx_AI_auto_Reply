"""Test script for OCR."""
import sys
sys.path.insert(0, ".")

from PIL import Image, ImageDraw, ImageFont
import mss


def test_screen_capture():
    """Test screen capture."""
    print("=== 测试屏幕截图 ===\n")

    with mss.mss() as sct:
        # Capture full screen
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        # Save screenshot
        output_path = "test_screenshot.png"
        img.save(output_path)
        print(f"✓ 截图已保存: {output_path}")
        print(f"  尺寸: {img.size}")

    return img


def test_ocr(image_path=None):
    """Test OCR recognition."""
    print("\n=== 测试 OCR ===\n")

    try:
        from cnocr import CnOcr
        ocr = CnOcr()
        print("✓ OCR 引擎初始化成功\n")

        if image_path:
            img = Image.open(image_path)
        elif image_path is None:
            # Use captured screenshot
            try:
                img = Image.open("test_screenshot.png")
            except FileNotFoundError:
                print("✗ 没有找到截图文件，请先运行屏幕截图测试")
                return None

        # Do OCR
        results = ocr.ocr(img)

        print("识别结果:")
        for i, line in enumerate(results):
            if line and "text" in line:
                print(f"  {i+1}. {line['text']}")

        if not results:
            print("  (无识别结果)")

        return results

    except Exception as e:
        print(f"✗ OCR 测试失败: {e}")
        return None


def test_ocr_on_region():
    """Test OCR on a specific region."""
    print("\n=== 测试区域 OCR ===\n")
    print("请在微信中打开一个聊天窗口，确保有文字消息")
    print("然后按Enter继续...\n")

    input("按Enter继续: ")

    with mss.mss() as sct:
        # Let user define region
        print("截图已保存到 test_ocr_region.png")
        # Capture center portion for demo
        monitors = sct.monitors[1]
        region = {
            "left": monitors["width"] // 4,
            "top": monitors["height"] // 4,
            "width": monitors["width"] // 2,
            "height": monitors["height"] // 2,
        }
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save("test_ocr_region.png")
        print(f"区域: {region}")

    # Test OCR
    try:
        from cnocr import CnOcr
        ocr = CnOcr()
        results = ocr.ocr(img)

        print("\n识别结果:")
        for i, line in enumerate(results[:10]):  # Show first 10
            if line and "text" in line:
                print(f"  {line['text']}")

        return results
    except Exception as e:
        print(f"✗ OCR 失败: {e}")
        return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true", help="仅截图")
    parser.add_argument("--region", action="store_true", help="区域OCR测试")
    args = parser.parse_args()

    if args.capture:
        test_screen_capture()
    elif args.region:
        test_ocr_on_region()
    else:
        # Full test
        test_screen_capture()
        test_ocr()
        print("\n提示: 用 --region 测试指定区域 OCR")