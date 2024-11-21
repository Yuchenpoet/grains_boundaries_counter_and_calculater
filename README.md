# GrainAnalyzer

**GrainAnalyzer** 是一个基于 Python 和 OpenCV 的图像处理工具，用于晶粒图像的分析与边界检测。用户可以通过交互式界面上传图像、动态调整超参数，并实时显示边界检测结果。该工具适用于材料科学中的晶粒结构分析和其他区域检测任务。

**GrainAnalyzer** is a Python and OpenCV-based image processing tool designed for grain image analysis and boundary detection. Users can upload images, dynamically adjust hyperparameters, and view real-time boundary detection results through an interactive interface. This tool is ideal for grain structure analysis in material science and other region detection tasks. It also allows users to draw, analyze, and measure areas interactively through a GUI. It is particularly useful for particle or region analysis tasks and supports user-defined pixel-to-physical unit (e.g., cm) ratios to calculate actual areas.

---

## 功能特点 / Features

- **图像加载和显示 / Image Loading and Display**：支持用户上传图片，并在界面中显示原始图像和处理后的结果图像。  
  Supports uploading images and displaying both the original and processed results.

- **高级形态学操作 / Advanced Morphological Operations**：通过高级形态学滤波清理噪声，提升边界检测结果的准确性。  
  Uses advanced morphological filtering to clean noise and improve boundary detection accuracy.

- **动态超参数调整 / Dynamic Hyperparameter Adjustment**：通过滑块动态调整图像处理参数，包括模糊核大小、阈值、区域最小面积等。  
  Dynamically adjust image processing parameters such as blur size, thresholds, and minimum area using sliders.

- **边界检测 / Boundary Detection**：实时显示晶粒边界，支持通过颜色高亮标注检测到的区域。  
  Real-time display of grain boundaries with color highlighting for detected regions.

- **缩放和导航 / Zoom and Navigation**：支持鼠标滚轮缩放图像。  
  Supports zooming in and out using the mouse wheel.

- **手动绘图 / Manual Drawing**：支持用户在图像上手动绘制区域（绿色线条）。  
  Allows users to draw regions manually on the image (green lines).

- **撤销功能 / Undo**：可以撤销上一次绘图操作。  
  Allows undoing the last drawing operation.

- **区域分析 / Region Analysis**：分析绘制后的区域，计算前 K 大区域的面积。  
  Analyzes the drawn regions and calculates the area of the top K largest regions.

- **面积单位换算 / Area Unit Conversion**：支持用户自定义像素与厘米的比例，计算实际面积（单位为 cm²）。  
  Supports user-defined pixel-to-cm ratios to calculate actual area (in cm²).

- **结果可视化 / Results Visualization**：将分析结果（包括面积和区域编号）直接标注在图像上。  
  Visualizes analysis results (including areas and region numbers) directly on the image.

- **图像保存 / Save Image**：支持保存带有分析结果的图像。  
  Allows saving the image with analysis results.

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

## 示例 / Examples

### 原图 / Original Image

以下是加载的原始晶粒图像：  
Below is the uploaded original grain image:

![origin](1.jpg)

---

### 检测结果 / Detected Result

以下是根据调整的超参数生成的边界检测结果：  
Below is the boundary detection result based on adjusted hyperparameters:

![result](result.jpg)

## 参数说明 / Parameter Description

| 参数名称 / Parameter Name       | 类型 / Type   | 默认值 / Default Value | 范围 / Range              | 作用 / Description                                                                 |
|---------------------------------|---------------|------------------------|---------------------------|-----------------------------------------------------------------------------------|
| **Blur Size**                   | 整数 / Integer | 5                      | 1 - 11（需为奇数） / Odd numbers between 1 - 11 | 控制高斯模糊的核大小，用于平滑图像，减少噪声的影响。  <br> Controls the Gaussian blur kernel size for smoothing the image and reducing noise. |
| **Block Size**                  | 整数 / Integer | 21                     | 3 - 51（需为奇数） / Odd numbers between 3 - 51 | 自适应阈值的局部块大小，值越大，局部阈值计算的范围越宽。 <br> Local block size for adaptive thresholding. Larger values widen the local thresholding range. |
| **Constant Subtract**           | 整数 / Integer | 2                      | 0 - 10                   | 自适应阈值中减去的常量值，用于微调分割效果。 <br> Constant subtracted in adaptive thresholding for fine-tuning the segmentation result.          |
| **Bilateral Filter Size**       | 整数 / Integer | 75                     | 0 - 200                  | 双边滤波器的大小，用于同时减少噪声并保留边缘细节。 <br> Size of the bilateral filter to reduce noise while preserving edge details.               |
| **Min Area**                    | 整数 / Integer | 50                     | 1 - 3000                 | 最小检测区域的面积，用于过滤掉较小的噪声区域。 <br> Minimum area for detected regions to filter out smaller noise regions.                          |
