"""
微信聊天OCR识别模块
根据文字颜色/背景颜色区分对方和自己的消息
"""

import io
import numpy as np
from PIL import Image
import cv2


class WeChatOCR:
    def __init__(self):
        self._ocr_engine = None

    @property
    def ocr_engine(self):
        if self._ocr_engine is None:
            import easyocr
            self._ocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
        return self._ocr_engine

    def recognize(self, image_data):
        """识别微信聊天图片中的对话内容"""
        img = self._load_image(image_data)
        if img is None:
            return {"success": False, "error": "无法加载图片"}

        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        h, w = cv_img.shape[:2]
        mid = w // 2

        # 左半边（通常是对方的消息）
        left_col = cv_img[:, :mid]
        # 右半边（通常是我的消息）
        right_col = cv_img[:, mid:]

        messages = []

        # 左边列消息
        for row in self._extract_individual_messages(left_col):
            speaker = self._detect_speaker(row)
            text = self._ocr_text(row)
            if text.strip():
                messages.append({"speaker": speaker, "content": text.strip()})

        # 右边列消息
        for row in self._extract_individual_messages(right_col):
            speaker = self._detect_speaker(row)
            text = self._ocr_text(row)
            if text.strip():
                messages.append({"speaker": speaker, "content": text.strip()})

        return {"success": True, "messages": messages}

    def _load_image(self, image_data):
        if isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            return Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            return Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            return image_data
        return None

    def _extract_individual_messages(self, col_img):
        """从一列中提取独立的每条消息"""
        h, w = col_img.shape[:2]

        # 检测每个连通域作为独立消息
        gray = cv2.cvtColor(col_img, cv2.COLOR_BGR2GRAY)

        # 只处理较亮的区域（即不是纯绿色背景的）
        # 文字和浅色背景都偏亮
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # 形态学操作连接文字
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
        dilated = cv2.dilate(binary, kernel, iterations=1)

        # 找连通域
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 排序（Y坐标）
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

        result = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 400:  # 过滤噪点
                continue

            x, y, cw, ch = cv2.boundingRect(c)

            # 消息行高太小忽略
            if ch < 15:
                continue

            margin = 2
            ny = max(0, y - margin)
            nh = min(h - ny, ch + margin * 2)

            if nh > 15 and cw > 30:  # 过滤太小的
                result.append(col_img[ny:ny+nh, :])

        return result

    def _detect_speaker(self, msg_img):
        """根��颜色检测说话人"""
        hsv = cv2.cvtColor(msg_img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(msg_img, cv2.COLOR_BGR2GRAY)
        h, w = msg_img.shape[:2]
        total = h * w

        # 绿色检测
        green = cv2.countNonZero(cv2.inRange(hsv, np.array([20, 20, 20]), np.array([100, 255, 255])))

        # 浅色背景检测
        light = cv2.countNonZero(cv2.inRange(gray, 245, 255))

        # 深色文字检测
        dark = cv2.countNonZero(cv2.inRange(gray, 0, 100))

        if green / total > 0.03:
            return "我"

        if light / total > 0.03 and dark > 0:
            return "对方"

        return "对方"

    def _ocr_text(self, msg_img):
        rgb = cv2.cvtColor(msg_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        results = self.ocr_engine.readtext(np.array(pil))

        texts = []
        for box, text, conf in results:
            if conf > 0.2:
                y_pos = min([p[1] for p in box])
                texts.append((y_pos, text))

        texts.sort(key=lambda x: x[0])
        return ''.join([t[1] for t in texts])


def recognize_wechat_chat(image_data):
    return WeChatOCR().recognize(image_data)


if __name__ == "__main__":
    import os
    for img in sorted(os.listdir("test_img")):
        if img.endswith(".png"):
            print(f"\n{img}")
            result = recognize_wechat_chat(f"test_img/{img}")
            if result["success"]:
                for m in result["messages"]:
                    print(f"  {m['speaker']}: {m['content']}")