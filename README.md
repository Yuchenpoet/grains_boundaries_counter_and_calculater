# GrainAnalyzer

**GrainAnalyzer** 是一个基于 Python 和 OpenCV 的图像分析工具，允许用户通过交互式 GUI 对图像进行绘制、分析和测量。该工具特别适用于粒子或区域分析任务，并支持用户定义像素与物理单位（如厘米）的比例，从而计算实际面积。

**GrainAnalyzer** is a Python and OpenCV-based image analysis tool that allows users to draw, analyze, and measure areas interactively through a GUI. It is particularly useful for particle or region analysis tasks and supports user-defined pixel-to-physical unit (e.g., cm) ratios to calculate actual areas.

---

## 功能特点 / Features

- **手动绘图 / Manual Drawing**：支持用户在图像上手动绘制区域（绿色线条）。  
  Allows users to draw regions manually on the image (green lines).

- **撤销功能 / Undo**：可以撤销最后一次绘图操作。  
  Allows undoing the last drawing operation.

- **区域分析 / Region Analysis**：分析绘制后的区域，计算前 K 大区域的面积。  
  Analyzes the drawn regions and calculates the area of the top K largest regions.

- **面积单位换算 / Area Unit Conversion**：支持用户自定义像素与厘米的比例，计算实际面积（单位为 cm²）。  
  Supports user-defined pixel-to-cm ratios to calculate actual area (in cm²).

- **结果可视化 / Results Visualization**：将分析结果（包括面积和区域编号）直接标注在图像上。  
  Visualizes analysis results (including areas and region numbers) directly on the image.

- **图像保存 / Save Image**：支持保存带有分析结果的图像。  
  Allows saving the image with analysis results.

- **缩放和导航 / Zoom and Navigation**：支持鼠标滚轮缩放图像。  
  Supports zooming in and out using the mouse wheel.

---

## 安装和运行 / Installation and Usage

### 环境依赖 / Dependencies

在运行该项目之前，请确保已安装以下依赖项：  
Before running the project, ensure the following dependencies are installed:

- Python 3.7 或更高版本 / Python 3.7 or higher
- OpenCV (`cv2`)
- NumPy
- Pillow
- Tkinter（Python 内置 / Built-in for Python）

可以通过以下命令安装所需依赖：  
Install the required dependencies using the following command:

```bash
pip install opencv-python-headless numpy pillow
