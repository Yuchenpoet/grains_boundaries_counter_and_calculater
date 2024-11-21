import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from counter import GrainAnalyzer as DrawingGrainAnalyzer


class GrainAnalyzer:
    def __init__(self, root):
        self.root = root
        self.image = None
        self.processed_image = None
        self.contours = None
        self.zoom_scale = 1.0  # 缩放比例
        self.image_offset = (0, 0)  # 图像偏移（用于缩放后居中显示）

        # 初始化 GUI
        self.setup_gui()

    def setup_gui(self):
        """设置主 GUI 布局"""
        self.root.title("Grain Analyzer")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # 左侧控制面板
        control_frame = tk.Frame(self.root, width=300, bg="lightgray")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 右侧图像显示区域
        self.image_canvas = tk.Canvas(self.root, bg="white")
        self.image_canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 绑定鼠标滚轮事件用于缩放
        self.image_canvas.bind("<MouseWheel>", self.zoom_image)

        # 控制面板内容
        tk.Button(control_frame, text="Load Image", command=self.load_image, bg="lightblue").pack(pady=10, fill=tk.X)
        tk.Button(control_frame, text="Clear", command=self.clear, bg="red", fg="white").pack(pady=10, fill=tk.X)
        tk.Button(control_frame, text="Analyze", command=self.analyze_image, bg="green", fg="white").pack(pady=10, fill=tk.X)

        # 滑块参数
        self.blur_size_var = tk.IntVar(value=5)
        self.block_size_var = tk.IntVar(value=21)
        self.const_subtract_var = tk.IntVar(value=2)
        self.bilateral_size_var = tk.IntVar(value=75)
        self.min_area_var = tk.IntVar(value=50)

        # 添加滑块
        self.add_slider(control_frame, "Blur Size", self.blur_size_var, 1, 11, self.update_image, step=2)
        self.add_slider(control_frame, "Block Size", self.block_size_var, 3, 51, self.update_image, step=2)
        self.add_slider(control_frame, "Constant Subtract", self.const_subtract_var, 0, 10, self.update_image)
        self.add_slider(control_frame, "Bilateral Filter Size", self.bilateral_size_var, 0, 200, self.update_image, step=5)
        self.add_slider(control_frame, "Min Area", self.min_area_var, 1, 3000, self.update_image, step=10)

    def add_slider(self, parent, label, variable, from_, to, command, step=1):
        """添加带标签的滑块"""
        frame = tk.Frame(parent, bg="lightgray")
        frame.pack(pady=5, fill=tk.X)

        tk.Label(frame, text=label, bg="lightgray").pack(anchor="w")
        slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal", variable=variable, command=lambda v: command())
        slider.pack(fill=tk.X)

    def load_image(self):
        """加载图像文件"""
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.png *.jpeg *.tiff *.bmp")]
        )
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if self.image is not None:
                self.zoom_scale = 1.0  # 重置缩放比例
                self.image_offset = (0, 0)  # 重置偏移
                self.show_image(self.image)
            else:
                messagebox.showerror("Error", "Failed to load image!")

    def clear(self):
        """清空图像和数据"""
        self.image = None
        self.processed_image = None
        self.contours = None
        self.image_canvas.delete("all")
        self.zoom_scale = 1.0  # 重置缩放比例
        self.image_offset = (0, 0)  # 重置偏移
        messagebox.showinfo("Info", "Cleared all data!")

    def process_image(self):
        """处理图像"""
        if self.image is None:
            messagebox.showerror("Error", "Please load an image first!")
            return

        # 确保核大小是奇数
        blur_size = max(1, self.blur_size_var.get() if self.blur_size_var.get() % 2 != 0 else self.blur_size_var.get() + 1)
        block_size = self.block_size_var.get() if self.block_size_var.get() % 2 != 0 else self.block_size_var.get() + 1
        const_subtract = self.const_subtract_var.get()
        bilateral_size = self.bilateral_size_var.get()
        min_area = self.min_area_var.get()

        # 图像处理
        bilateral = cv2.bilateralFilter(self.image, 9, bilateral_size, bilateral_size)

        # 自适应阈值
        thresh_bilateral = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, block_size, const_subtract
        )

        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned_thresh = cv2.morphologyEx(thresh_bilateral, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned_thresh = cv2.morphologyEx(cleaned_thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # 查找轮廓
        contours, _ = cv2.findContours(cleaned_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 按区域过滤轮廓
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]
        self.contours = contours  # 存储所有轮廓以便动态更新

        # 在原始图像上绘制轮廓
        contour_img = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_img, filtered_contours, -1, (0, 255, 0), thickness=10)  # 绿色轮廓

        # 保存处理后的图像
        self.processed_image = contour_img

        return contour_img

    def update_image(self):
        """实时更新图像显示"""
        if self.image is None:
            return

        processed_img = self.process_image()
        if processed_img is not None:
            self.show_image(processed_img)

    def show_image(self, image):
        """在 Canvas 上显示图像"""
        # 根据缩放比例调整图像大小
        zoomed_image = cv2.resize(image, None, fx=self.zoom_scale, fy=self.zoom_scale, interpolation=cv2.INTER_LINEAR)

        # 转换为 RGB 格式
        image_rgb = cv2.cvtColor(zoomed_image, cv2.COLOR_BGR2RGB) if len(zoomed_image.shape) == 3 else cv2.cvtColor(zoomed_image, cv2.COLOR_GRAY2RGB)
        image_pil = Image.fromarray(image_rgb)

        # 动态调整 Canvas 的大小以适应图片
        self.image_canvas.config(scrollregion=(0, 0, image_pil.width, image_pil.height))
        image_tk = ImageTk.PhotoImage(image_pil)

        self.image_canvas.delete("all")
        self.image_canvas.create_image(self.image_offset[0], self.image_offset[1], image=image_tk, anchor="nw")
        self.image_canvas.image = image_tk  # 防止垃圾回收

    def zoom_image(self, event):
        """通过鼠标滚轮缩放图像"""
        if self.image is None:
            return

        # 更新缩放比例
        scale_step = 0.1
        if event.delta > 0:  # 滚轮向上滚动
            self.zoom_scale += scale_step
        elif event.delta < 0:  # 滚轮向下滚动
            self.zoom_scale = max(self.zoom_scale - scale_step, 0.1)  # 防止缩放比例过小

        self.show_image(self.processed_image if self.processed_image is not None else self.image)

    def analyze_image(self):
        """将处理后的图像传递到绘图接口中"""
        if self.processed_image is None:
            messagebox.showerror("Error", "Please process an image first!")
            return

        # 启动新的 GrainAnalyzer 界面（绘图模式接口）
        new_root = tk.Toplevel(self.root)
        drawing_analyzer = DrawingGrainAnalyzer(new_root)

        # 将当前处理后的图像传递给绘图接口
        drawing_analyzer.load_from_image(self.processed_image)  # 使用直接加载图像的方法
        new_root.mainloop()


def main():
    root = tk.Tk()
    app = GrainAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()