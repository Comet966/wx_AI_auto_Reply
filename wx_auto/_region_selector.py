"""
_region_selector.py
鼠标区域选择工具 - 用于OCR前选区定义
通过点击-拖拽-释放手势选择矩形区域，输出坐标供OCR使用
"""

import tkinter as tk
import json
import os
import sys


class RegionSelector:
    """全屏矩形选区选择器"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 半透明背景
        self.root.configure(bg='black')

        # 选区状态
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.selection_rect = None

        # 创建画布用于绘制选区
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.root.bind('<Escape>', self.cancel_selection)

        # 信息标签
        self.info_label = tk.Label(
            self.root,
            text='拖拽选择区域 | ESC取消',
            fg='white',
            bg='#333333',
            font=('Arial', 14),
            padx=20,
            pady=10
        )
        self.info_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # 全屏覆盖层（使背景变暗）
        self.canvas.create_rectangle(
            0, 0, 5000, 5000,
            fill='black', outline=''
        )

        # 隐藏提示文字在顶层之后
        self.info_label.lift()

    def normalize_coords(self, x1, y1, x2, y2):
        """规范化坐标：处理右上角拖拽等反向情况"""
        return (
            min(x1, x2),
            min(y1, y2),
            max(x1, x2),
            max(y1, y2)
        )

    def on_mouse_down(self, event):
        """鼠标按下：记录起始点"""
        self.start_x = event.x
        self.start_y = event.y
        print(f"[选区] 开始点: ({self.start_x}, {self.start_y})")

    def on_mouse_move(self, event):
        """鼠标移动：更新选区预览"""
        self.current_x = event.x
        self.current_y = event.y

        # 删除旧选区
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        # 计算规范化的矩形坐标
        x1, y1, x2, y2 = self.normalize_coords(
            self.start_x, self.start_y,
            self.current_x, self.current_y
        )

        # 绘制新选区（绿色边框，无填充）
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='#00FF00',
            width=3,
            fill=''  # 无填充
        )

        # 更新尺寸显示
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        self.info_label.config(
            text=f'选区: {width}x{height} | 起点({x1},{y1})'
        )

    def on_mouse_up(self, event):
        """鼠标释放：完成选区"""
        if self.start_x is None:
            return

        # 计算最终坐标
        x1, y1, x2, y2 = self.normalize_coords(
            self.start_x, self.start_y,
            event.x, event.y
        )

        # 检查最小选区大小（防止��触）
        width = x2 - x1
        height = y2 - y1

        if width < 10 or height < 10:
            print("[!] 选区太小，请重新选择")
            self.reset_selection()
            return

        # 显示结果并退出
        self.show_result(x1, y1, x2, y2, width, height)

    def show_result(self, x1, y1, x2, y2, width, height):
        """显示结果并写入文件"""
        self.root.attributes('-alpha', 1.0)  # 不透明，显示结果

        # 控制台输出
        print("\n" + "="*50)
        print("选区选择完成!")
        print("="*50)
        print(f"左上角: ({x1}, {y1})")
        print(f"右下角: ({x2}, {y2})")
        print(f"宽度: {width} 像素")
        print(f"高度: {height} 像素")

        # JSON格式输出
        result = {
            "x": x1,
            "y": y1,
            "width": width,
            "height": height,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }

        # 写入result.json供后续OCR使用
        result_path = os.path.join(os.path.dirname(__file__), 'selection_result.json')
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        print(f"\n结果已保存至: {result_path}")
        print(json.dumps(result, indent=2))

        # 3秒后自动退出
        self.root.after(3000, lambda: self.root.destroy())

    def cancel_selection(self, event=None):
        """取消选择"""
        print("[!] 已取消选择")
        self.root.destroy()

    def reset_selection(self):
        """重置选区状态"""
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        self.start_x = None
        self.start_y = None

    def run(self):
        """启动选择器"""
        print("[选区] 按住鼠标左键拖拽选择区域，ESC取消")
        self.root.mainloop()


def main():
    """主入口"""
    selector = RegionSelector()
    selector.run()


if __name__ == '__main__':
    main()