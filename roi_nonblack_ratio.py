import os
import cv2
import numpy as np
import pandas as pd
from glob import glob

# 设置参数
folder_path = "014/left/filtered_data_L14-55"  # 示例路径
x, y, w, h = 92, 197, 177, 65  # 你指定的 ROI 区域

# 获取所有 PNG 文件
image_files = sorted(glob(os.path.join(folder_path, "*.png")))

# 准备结果列表
results = []

# 遍历每张图片
for image_path in image_files:
    img = cv2.imread(image_path)
    if img is None:
        continue

    # 提取 ROI
    roi = img[y:y+h, x:x+w]

    # 判断黑色像素
    is_black = np.all(roi == [0, 0, 0], axis=-1)
    black_pixels = int(np.sum(is_black))
    color_pixels = int(roi.shape[0] * roi.shape[1] - black_pixels)
    ratio = color_pixels / (roi.shape[0] * roi.shape[1])

    filename = os.path.basename(image_path)
    results.append([filename, black_pixels, color_pixels, ratio])

# 保存为 Excel 表格
df = pd.DataFrame(results, columns=["filename", "black_pixels", "color_pixels", "non_black_ratio"])
excel_path = "roi_pixel_stats.xlsx"
df.to_excel(excel_path, index=False)


