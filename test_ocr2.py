"""Test OCR on captured screenshot."""
from PIL import Image
from cnocr import CnOcr

print("=== 测试 OCR ===\n")

# Initialize OCR
ocr = CnOcr()
print("✓ OCR 引擎初始化成功\n")

# Load captured screenshot
try:
    img = Image.open("test_screenshot.png")
    print(f"图片尺寸: {img.size}")
except FileNotFoundError:
    print("✗ 没有截图文件")
    exit(1)

# Run OCR
print("正在识别...")
results = ocr.ocr(img)

print(f"\n共识别到 {len(results)} 行:\n")
for i, line in enumerate(results):
    if line and "text" in line:
        print(f"{i+1}. {line['text']}")

if not results:
    print("(无识别结果)")