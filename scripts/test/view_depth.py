import cv2
import os
import numpy as np
import time
# 设置深度图像和RGB图像文件夹路径
depth_folder = "/media/hg/新加卷/Agrosense/data/001/right/dep_data_R001"
rgb_folder = "/media/hg/新加卷/Agrosense/data/001/right/rgb_data_R001"

# 获取排序后的文件列表
depth_files = sorted([f for f in os.listdir(depth_folder) if f.endswith(('.png', '.tiff', '.jpg'))])
rgb_files = sorted([f for f in os.listdir(rgb_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])  # 仅RGB格式

# 形态学滤波的核大小
kernel = np.ones((5, 5), np.uint8)  # 5x5 结构元素，适用于小缝隙

# 设置深度值范围（单位可能是毫米，根据你的深度图像格式调整）
depth_min = 0  # 3.5 米（最小保留深度）
depth_max = 3500  # 最大深度，比如 10 米（可调整）

index = 3200  # 从第 733 张图片开始

while 0 <= index < len(depth_files):  # 确保索引有效
    depth_file = depth_files[index]
    depth_path = os.path.join(depth_folder, depth_file)

    # **找到对应的 RGB 图像**
    rgb_path = os.path.join(rgb_folder, depth_file.replace("_depth", ""))
    if not os.path.exists(rgb_path):
        print(f"未找到对应的RGB图像: {rgb_path}")
        index += 1  # 跳过当前，显示下一张
        continue

    # 读取深度图像（假设是16位深度图像）
    depth_image = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
    rgb_image = cv2.imread(rgb_path, cv2.IMREAD_COLOR)  # 读取RGB图像

    if depth_image is None or rgb_image is None:
        print(f"无法读取 {depth_file} 或 {rgb_path}")
        index += 1
        continue
    
    print(index)
    # **剪切深度范围，仅保留 3.5 米以上的深度**
    depth_clipped = np.where((depth_image <= depth_max), depth_image, 0)

    # **应用形态学处理来填补小缝隙**
    depth_morphed = cv2.morphologyEx(depth_clipped, cv2.MORPH_CLOSE, kernel)  # 闭运算填补缝隙
    depth_morphed = cv2.morphologyEx(depth_morphed, cv2.MORPH_OPEN, kernel)  # 开运算去除小噪声

    # **归一化深度图像到0-255范围，方便伪彩色映射**
    depth_normalized = cv2.normalize(depth_morphed, None, 0, 255, cv2.NORM_MINMAX)
    depth_normalized = np.uint8(depth_normalized)  # 转换为8位图像

    # **应用伪彩色映射**
    depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

    # **将背景（值为0的区域）设置为纯黑**
    depth_colormap[depth_morphed == 0] = [0, 0, 0]

    # **调整RGB图像大小以匹配深度图**
    rgb_resized = cv2.resize(rgb_image, (depth_colormap.shape[1], depth_colormap.shape[0]))

    # **拼接RGB和深度图**
    combined_image = cv2.hconcat([rgb_resized, depth_colormap])

    # **显示RGB + 深度**
    cv2.imshow("RGB & Depth", combined_image)
    cv2.waitKey(1)
    # **等待用户输入按键**
    key = cv2.waitKey(0)  # 等待用户按键
    print(f"按键值: {key}")  # **打印按键值，检查是否正确读取**

    if key == ord('d') or key == 39:  # → 右箭头 或 'D' 键（下一张）
        print(index)
        index = min(index + 1, len(depth_files) - 1)  # 确保 index 不超过最大值
        print(index)
    elif key == ord('a') or key == 37:  # ← 左箭头 或 'A' 键（上一张）
        print(index)
        index = max(index - 1, 0)  # 确保 index 不小于 0
        print(index)
    elif key == 27:  # ESC 键退出
        cv2.destroyAllWindows()
        exit()
# 关闭窗口
cv2.destroyAllWindows()
