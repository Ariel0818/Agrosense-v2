import cv2
import numpy as np
import matplotlib.pyplot as plt

# 读取深度图像（16位PNG）
depth_img = cv2.imread('013/right/dep_data_R13/0000244_depth.png', cv2.IMREAD_ANYDEPTH)
if depth_img is None:
    print("无法加载深度图像，请检查文件路径。")
    exit()

# 将深度图像归一化到0-255
depth_norm = cv2.normalize(depth_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

# 反转归一化图像，使得深度值越小（近）对应的像素值越大（浅），深度值越大（远）对应的像素值越小（深）
depth_inverted = 255 - depth_norm

# 方式一：直接显示灰度图
plt.figure(figsize=(10, 8))
plt.imshow(depth_inverted, cmap='gray')
plt.title('深度图像可视化 - 灰度图 (近处浅，远处深)')
plt.axis('off')
plt.show()

# 方式二：应用伪彩色映射后显示
depth_color = cv2.applyColorMap(depth_inverted, cv2.COLORMAP_JET)
plt.figure(figsize=(10, 8))
# 注意：OpenCV 默认颜色顺序为 BGR，转换为 RGB 显示正确颜色
plt.imshow(cv2.cvtColor(depth_color, cv2.COLOR_BGR2RGB))
plt.title('深度图像可视化 - 伪彩色 (近处浅，远处深)')
plt.axis('off')
plt.show()
