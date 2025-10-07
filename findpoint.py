# -*- coding: utf-8 -*-
"""
功能：
- 在 RGB 图上鼠标点选获取 (x, y)
- 在 'depth_dir' 中用同名文件找到对应深度图
- 用 (x, y) 读取深度图像素的 depth 值（保留原始位深；自动尺寸映射）

使用：
- 修改 rgb_path 和 depth_dir，然后运行
- 在弹出的图上点击一次目标像素，按回车结束
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------- 用户需要修改的输入 -----------
rgb_path = Path("/Volumes/LaCie/Agrosense2/data_2025_7_22/data/250122075706/20250714_2046/rgb/20250715_005314_006832.png")
depth_path = Path("/Volumes/LaCie/Agrosense2/data_2025_7_22/data/250122075706/20250714_2046/depth/20250715_005314_006832.png")
# ----------------------------------------

def imread_rgb_for_show(p: Path):
    """cv2 读取并转为 RGB（用于显示）。"""
    img_bgr = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise FileNotFoundError(f"无法读取RGB图像：{p}")
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def imread_depth_raw(p: Path):
    """读取深度图，保持原始位深（如16-bit PNG）。"""
    depth = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if depth is None:
        raise FileNotFoundError(f"无法读取深度图：{p}")
    if depth.ndim == 3 and depth.shape[2] > 1:  # 兜底：若被读成多通道，转灰度
        depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
    return depth


def pick_point_and_read_depth(rgb_path: Path, depth_dir: Path):
    # 读取 RGB
    img_rgb = imread_rgb_for_show(rgb_path)
    h, w = img_rgb.shape[:2]

    # 交互点选
    plt.figure()
    plt.imshow(img_rgb)
    plt.title("find a point and press/Enter")
    plt.axis('on')
    pts = plt.ginput(n=1, timeout=0)  # 返回 [(x, y)]
    plt.close()

    if not pts:
        print("未获取到点击点。")
        return

    x, y = pts[0]
    x_i, y_i = int(round(x)), int(round(y))
    x_i = max(0, min(w - 1, x_i))
    y_i = max(0, min(h - 1, y_i))
    print(f"点击坐标 (x, y) = ({x_i}, {y_i})，RGB尺寸 = ({w}, {h})")


    # 读取深度
    depth = imread_depth_raw(depth_path)

    depth_val = depth[y_i, x_i]
    print(f"Depth 值 = {depth_val} (dtype={depth.dtype})")

    # 可视化标注（可选）
    plt.figure()
    plt.imshow(img_rgb)
    plt.scatter([x_i], [y_i], s=60, marker='x')
    plt.title(f"点击点 (x={x_i}, y={y_i}), depth={depth_val}")
    plt.show()

if __name__ == "__main__":
    pick_point_and_read_depth(rgb_path, depth_path)
