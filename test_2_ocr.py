"""测试 2: OCR 识别"""
from PIL import Image
from cnocr import CnOcr
import mss

print("=" * 50)
print("测试 OCR 识别")
print("=" * 50)

# Step 1: 检查是否有现成截图
import os
if os.path.exists("test_screenshot.png"):
    img = Image.open("test_screenshot.png")
    print(f"[1] 加载现有截图: {img.size}")
else:
    print("[1] 捕获新截图...")
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    print(f"[1] 截图完成: {img.size}")

print()

# Step 2: 初始化 OCR 引擎
print("[2] 初始化 OCR 引擎...")
ocr = CnOcr()
print("[2] OCR 引擎就绪\n")

# Step 3: 执行识别
print("[3] 正在识别文字...\n")
results = ocr.ocr(img)

print("-" * 50)
print(f"识别结果 (共 {len(results)} 行):\n")
for i, line in enumerate(results[:20]):  # 只显示前20行
    if line and "text" in line:
        print(f"  {i+1}. {line['text']}")
if len(results) > 20:
    print(f"  ... 还有 {len(results)-20} 行")
print("-" * 50)
print(f"\n✓ OCR 识别完成")