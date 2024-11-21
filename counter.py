import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk, ImageDraw


class GrainAnalyzer:
    def __init__(self, root, initial_image=None):
        self.root = root
        self.image = None
        self.processed_image = None
        self.drawing_image = None
        self.zoom_scale = 1.0
        self.image_offset = (0, 0)
        self.num_regions = tk.IntVar(value=10)  # 默认显示 Top K
        self.average_area = tk.DoubleVar(value=0.0)  # Top K 平均面积
        self.pixel_per_cm = tk.DoubleVar(value=1.0)  # 像素/厘米比例，默认 1
        self.draw_mode = False
        self.last_position = (None, None)
        self.pil_image = None
        self.draw = None

        self.draw_history = []  # 用于记录绘图历史（撤销操作的单位）
        self.current_drawing_backup = None  # 用于记录鼠标按下时的图像状态
        self.setup_gui()

        # 如果传入了初始图像，则直接加载
        if initial_image is not None:
            self.load_from_image(initial_image)

    def setup_gui(self):
        """设置主 GUI 布局"""
        self.root.title("Grain Analyzer with Draw & Analyze Functionality")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # 左侧控制面板
        control_frame = tk.Frame(self.root, width=300, bg="lightgray")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 右侧图像显示区域
        self.image_canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.image_canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 绑定鼠标事件
        self.image_canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.image_canvas.bind("<B1-Motion>", self.draw_line)
        self.image_canvas.bind("<ButtonRelease-1>", self.end_drawing)  # 鼠标松开时记录绘图
        self.image_canvas.bind("<MouseWheel>", self.zoom_image)

        # 控制面板内容
        tk.Button(control_frame, text="Clear", command=self.clear, bg="red", fg="white").pack(pady=10, fill=tk.X)
        tk.Checkbutton(
            control_frame, text="Draw Mode", command=self.toggle_draw_mode, bg="orange"
        ).pack(pady=10, fill=tk.X)
        tk.Button(control_frame, text="Undo", command=self.undo_last_drawing, bg="yellow").pack(pady=10, fill=tk.X)  # 撤销按钮
        tk.Button(control_frame, text="Analyze", command=self.analyze_drawing, bg="green", fg="white").pack(pady=10, fill=tk.X)
        tk.Button(control_frame, text="Save Image", command=self.save_image, bg="blue", fg="white").pack(pady=10, fill=tk.X)

        # 像素/厘米输入框
        self.add_pixel_per_cm_input(control_frame)

        # 滑块：调整显示区域的数量
        self.add_slider(control_frame, "Number of Regions", self.num_regions, 1, 200, self.analyze_drawing)

        # 实时显示 Top K 平均面积
        self.average_area_label = tk.Label(
            control_frame, text=f"Avg Area: {self.average_area.get():.2f} cm²", bg="lightgray", font=("Arial", 12)
        )
        self.average_area_label.pack(pady=10, anchor="w")

    def add_pixel_per_cm_input(self, parent):
        """添加像素/厘米输入框"""
        frame = tk.Frame(parent, bg="lightgray")
        frame.pack(pady=10, fill=tk.X)

        tk.Label(frame, text="Pixels per cm:", bg="lightgray").pack(side=tk.LEFT, padx=5)
        entry = tk.Entry(frame, textvariable=self.pixel_per_cm, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        self.pixel_per_cm.set(1.0)  # 默认值为 1

    def add_slider(self, parent, label, variable, from_, to, command=None):
        """添加滑块"""
        frame = tk.Frame(parent, bg="lightgray")
        frame.pack(pady=5, fill=tk.X)

        self.slider_label = tk.Label(frame, text=f"{label}: {variable.get()}", bg="lightgray")
        self.slider_label.pack(anchor="w")

        slider = ttk.Scale(
            frame,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=variable,
            command=lambda v: [self.slider_label.config(text=f"{label}: {int(float(v))}"), command()]
            if command
            else self.slider_label.config(text=f"{label}: {int(float(v))}")
        )
        slider.pack(fill=tk.X)

    def load_from_image(self, image):
        """直接加载传入的 NumPy 图像数据"""
        self.image = image
        self.zoom_scale = 1.0
        self.image_offset = (0, 0)
        self.processed_image = None

        # 将 NumPy 图像转换为 PIL 图像，支持绘图
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(image_rgb)
        self.drawing_image = self.pil_image.copy()
        self.draw = ImageDraw.Draw(self.drawing_image)

        self.draw_history.clear()  # 清空绘图历史
        self.show_image(self.image)

    def clear(self):
        """清空绘图内容"""
        if self.pil_image is not None:
            self.drawing_image = self.pil_image.copy()
            self.draw = ImageDraw.Draw(self.drawing_image)
            self.draw_history.clear()  # 清空绘图历史
            self.update_canvas()
        else:
            messagebox.showinfo("Info", "No image to clear!")

    def toggle_draw_mode(self):
        """切换绘图模式"""
        self.draw_mode = not self.draw_mode
        self.image_canvas.config(cursor="pencil" if self.draw_mode else "arrow")

    def start_drawing(self, event):
        """记录鼠标按下时的图像状态"""
        if not self.draw_mode or self.drawing_image is None:
            return
        self.current_drawing_backup = self.drawing_image.copy()  # 保存当前图像状态
        x, y = self.canvas_to_image_coords(event.x, event.y)
        self.last_position = (x, y)

    def draw_line(self, event):
        """在图像上绘制线条"""
        if not self.draw_mode or self.drawing_image is None or self.last_position == (None, None):
            return

        x1, y1 = self.last_position
        x2, y2 = self.canvas_to_image_coords(event.x, event.y)

        # 绘制线条
        self.draw.line([x1, y1, x2, y2], fill=(0, 255, 0), width=10)

        self.last_position = (x2, y2)
        self.update_canvas()

    def end_drawing(self, event):
        """鼠标松开时，将整段绘图保存为一个撤销单位"""
        if self.current_drawing_backup is not None:
            self.draw_history.append(self.current_drawing_backup)  # 保存鼠标按下时的图像状态
            self.current_drawing_backup = None  # 清空备份状态
        self.last_position = (None, None)  # 重置鼠标位置

    def undo_last_drawing(self):
        """撤销最后一次绘图"""
        if self.draw_history:
            # 从历史记录中恢复上一个状态
            self.drawing_image = self.draw_history.pop()
            self.draw = ImageDraw.Draw(self.drawing_image)
            self.update_canvas()
        else:
            messagebox.showinfo("Info", "No more actions to undo!")

    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """将画布坐标转换为原始图像坐标"""
        image_x = int((canvas_x - self.image_offset[0]) / self.zoom_scale)
        image_y = int((canvas_y - self.image_offset[1]) / self.zoom_scale)
        return max(0, min(image_x, self.pil_image.width - 1)), max(0, min(image_y, self.pil_image.height - 1))

    def analyze_drawing(self, *_):
        """分析绘图后的图像"""
        if self.drawing_image is None:
            messagebox.showerror("Error", "No image to analyze!")
            return

        drawing_np = np.array(self.drawing_image)
        analyzed_image = self.analyze_regions(drawing_np)
        if analyzed_image is not None:
            self.processed_image = analyzed_image
            self.show_image(analyzed_image)

    def analyze_regions(self, image):
        """分析图像中的区域并标记前 K 大的区域"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)

        contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_areas = [(cv2.contourArea(cnt), cnt) for cnt in contours if cv2.contourArea(cnt) > 0]
        contour_areas.sort(key=lambda x: x[0], reverse=True)

        top_k = int(self.num_regions.get())
        top_contours = contour_areas[:top_k]

        total_area = sum(area for area, _ in top_contours)
        pixel_cm_ratio = self.pixel_per_cm.get()  # 获取像素/厘米比例
        area_in_cm2 = total_area / (pixel_cm_ratio ** 2)  # 换算为 cm²

        self.average_area.set(area_in_cm2 / top_k if top_k > 0 else 0.0)
        self.average_area_label.config(text=f"Avg Area: {self.average_area.get():.2f} cm²")

        result_image = image.copy()
        for i, (area, cnt) in enumerate(top_contours):
            cv2.drawContours(result_image, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                text = f"{i + 1}"
                (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                cv2.rectangle(result_image, (cx - tw // 2 - 5, cy - th - 5), (cx + tw // 2 + 5, cy + 5), (255, 255, 255), -1)
                cv2.putText(result_image, text, (cx - tw // 2, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

        return result_image

    def save_image(self):
        """保存当前处理的图像到文件"""
        if self.processed_image is None:
            messagebox.showerror("Error", "No processed image to save!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if save_path:
            image_with_text = self.processed_image.copy()
            text = f"Avg Area: {self.average_area.get():.2f} cm²"
            cv2.putText(image_with_text, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 5)
            cv2.putText(image_with_text, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
            cv2.imwrite(save_path, image_with_text)
            messagebox.showinfo("Info", f"Image saved to {save_path}")

    def update_canvas(self):
        """更新显示绘图后的图像"""
        self.show_image(np.array(self.drawing_image))

    def show_image(self, image):
        """在 Canvas 上显示图像"""
        zoomed_image = cv2.resize(image, None, fx=self.zoom_scale, fy=self.zoom_scale, interpolation=cv2.INTER_LINEAR)
        image_rgb = cv2.cvtColor(zoomed_image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        self.image_canvas.delete("all")
        self.image_canvas.create_image(self.image_offset[0], self.image_offset[1], image=image_tk, anchor="nw")
        self.image_canvas.image = image_tk

    def zoom_image(self, event):
        """通过鼠标滚轮缩放图像"""
        if self.image is None:
            return

        scale_step = 0.1
        if event.delta > 0:
            self.zoom_scale += scale_step
        elif event.delta < 0:
            self.zoom_scale = max(self.zoom_scale - scale_step, 0.1)

        self.update_canvas()


def open_editor_with_image(image):
    """暴露的函数：打开编辑器并自动加载传入的图像"""
    root = tk.Toplevel()
    app = GrainAnalyzer(root, initial_image=image)