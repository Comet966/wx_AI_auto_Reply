"""
screen_capture.py
指定坐标区域的屏幕截图工具
根据用户指定的 (x, y, width, height) 进行截图，并返回结果
"""

import mss
import os
import json
import numpy as np
from datetime import datetime


class ScreenCapture:
    """屏幕截图工具 - 根据指定坐标进行区域截图"""

    def __init__(self):
        self.mss = mss.mss()

    def capture_region(self, x, y, width, height, output_path=None, return_image=True):
        """
        根据指定区域进行截图

        Args:
            x: 截图区域左上角 X 坐标
            y: 截图区域左上角 Y 坐标
            width: 截图区域宽度
            height: 截图区域高度
            output_path: 可选，截图保存路径（PNG格式）
            return_image: 是否返回图像数据

        Returns:
            dict: 包含成功状态、图像数据和元信息的字典
        """
        # 参数验证
        if width <= 0 or height <= 0:
            return {
                "success": False,
                "error": f"无效的区域尺寸: width={width}, height={height}"
            }

        # 构建截图区域字典（mss 使用 left, top, width, height 格式）
        region = {
            "left": int(x),
            "top": int(y),
            "width": int(width),
            "height": int(height)
        }

        try:
            # 执行截图
            screenshot = self.mss.grab(region)

            # 准备返回值
            result = {
                "success": True,
                "region": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "format": "PNG"
                }
            }

            # 如果指定了输出路径，保存图片
            if output_path:
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # 保存为 PNG 文件
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_path)
                result["file_path"] = output_path
                result["metadata"]["saved"] = True

            # 返回图像数据（PNG 格式的字节串）
            if return_image:
                image_data = mss.tools.to_png(screenshot.rgb, screenshot.size)
                result["image_data"] = image_data
                result["image_base64"] = image_data.decode('latin-1') if isinstance(image_data, bytes) else image_data

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"截图失败: {str(e)}",
                "region": region
            }

    def capture_full_screen(self, monitor_index=1, output_path=None):
        """
        捕获整个屏幕（或指定显示器）

        Args:
            monitor_index: 显示器索引（1 = 主显示器）
            output_path: 可选，截图保存路径

        Returns:
            dict: 截图结果
        """
        # 获取所有显示器信息
        monitors = self.mss.monitors

        if monitor_index < 1 or monitor_index >= len(monitors):
            monitor_index = 1  # 默认���显示器

        monitor = monitors[monitor_index]
        return self.capture_region(
            x=monitor["left"],
            y=monitor["top"],
            width=monitor["width"],
            height=monitor["height"],
            output_path=output_path
        )

    def get_monitors(self):
        """获取所有显示器信息"""
        return self.mss.monitors

    def close(self):
        """关闭截图工具"""
        # mss 不需要显式关闭，但保留此接口以便未来扩展
        pass


def capture(x, y, width, height, output_path=None):
    """
    快捷截图函数

    Args:
        x: 截图区域左上角 X 坐标
        y: 截图区域左上角 Y 坐标
        width: 截图区域宽度
        height: 截图区域高度
        output_path: 可选，截图保存路径

    Returns:
        dict: 截图结果
    """
    capturer = ScreenCapture()
    result = capturer.capture_region(x, y, width, height, output_path)
    capturer.close()
    return result


if __name__ == "__main__":
    # 测试：捕获一个示例区域
    # 从命令行参数获取坐标，或使用默认值
    import sys

    if len(sys.argv) >= 5:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        width = int(sys.argv[3])
        height = int(sys.argv[4])
        output_file = sys.argv[5] if len(sys.argv) > 5 else None
    else:
        # 默认测试参数
        x, y, width, height = 100, 100, 400, 300
        output_file = "test_capture.png"

    print(f"正在截取区域: ({x}, {y}) {width}x{height}")
    result = capture(x, y, width, height, output_file)

    if result["success"]:
        print(f"截图成功!")
        print(f"区域: x={result['region']['x']}, y={result['region']['y']}, "
              f"width={result['region']['width']}, height={result['region']['height']}")
        print(f"时间戳: {result['metadata']['timestamp']}")

        if "file_path" in result:
            print(f"文件已保存至: {result['file_path']}")
    else:
        print(f"截图失败: {result.get('error')}")