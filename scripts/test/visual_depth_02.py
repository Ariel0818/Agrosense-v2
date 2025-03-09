import cv2
import numpy as np
import os

# 设置深度图像路径
depth_folder = "/media/hg/新加卷/Agrosense/data/001/right/dep_data_R001/0003004_depth.png"

# **读取深度图像（确保是16位或8位）**
depth_image = cv2.imread(depth_folder, cv2.IMREAD_UNCHANGED)

# **检查是否成功读取**
if depth_image is None:
    print(f"Error: Unable to read depth image from {depth_folder}")
    exit()

# **检查数据类型**
print(f"Depth Image dtype: {depth_image.dtype}, shape: {depth_image.shape}")

# **归一化深度图**
if depth_image.dtype == np.uint16:  # 16-bit depth image
    depth_image = depth_image.astype(np.float32)  # 转换为浮点数
    depth_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    depth_normalized = np.uint8(depth_normalized)  # 转换为 8 位
else:
    depth_normalized = depth_image  # 8-bit depth image 直接使用

# **伪彩色映射**
depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

# **创建窗口**
cv2.namedWindow("Depth Map", cv2.WINDOW_AUTOSIZE)

# **鼠标回调函数**
def show_depth(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:  # 仅在鼠标移动时更新
        if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:  # 避免越界
            depth_value = depth_image[y, x]  # **从原始深度图读取真实深度值**
            display_img = depth_colormap.copy()

            # **显示深度数值**
            text = f"Depth: {depth_value} mm"
            cv2.putText(display_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # **更新窗口**
            cv2.imshow("Depth Map", display_img)

# **绑定鼠标事件**
cv2.setMouseCallback("Depth Map", show_depth)

# **显示窗口**
cv2.imshow("Depth Map", depth_colormap)
cv2.waitKey(0)
cv2.destroyAllWindows()
