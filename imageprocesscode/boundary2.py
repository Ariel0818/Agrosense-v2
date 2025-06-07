import cv2
import numpy as np


# 1. 读取图像
img = cv2.imread('014/left/filtered_data_L14-55/0000142.png')  # 替换为你的图像路径
if img is None:
    raise ValueError("读取图像失败，请检查图像路径！")

# 2. 转换为灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 3. 使用高斯模糊去噪
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 4. 使用 Canny 边缘检测
edges = cv2.Canny(blur, 50, 150)

# 5. 利用 findContours 提取轮廓
# 注意：这一步仅对二值图（边缘图）进行轮廓提取
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 6. 绘制轮廓到原始图像
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

# 7. 显示结果
cv2.imshow("Detected Contours", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 4. 创建一个空白图像用于填充（或者直接在原图上绘制）
filled = np.zeros_like(img)

# 5. 将所有轮廓填充，thickness=-1 表示填充整个区域
cv2.drawContours(filled, contours, -1, (255, 255, 255), thickness=-1)

# 6. 显示结果
cv2.imshow("Filled Contours", filled)
cv2.waitKey(0)
cv2.destroyAllWindows()





# contour = max(contours, key=cv2.contourArea)

# # 可视化原始轮廓
# img_show = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
# cv2.drawContours(img_show, [contour], -1, (0, 255, 0), 2)
# cv2.imshow("Original Contour", img_show)
# cv2.waitKey(0)

# # 3. 计算凸包（返回索引形式）和凸性缺陷
# hull = cv2.convexHull(contour, returnPoints=False)
# if hull is None or len(hull) < 3:
#     print("凸包点不足")
#     exit()

# defects = cv2.convexityDefects(contour, hull)
# if defects is None:
#     print("未检测到凸性缺陷")
#     exit()

# # 4. 筛选出缺陷深度大于设定阈值的缺陷
# depth_threshold = 1000  # 根据实际情况调整
# defect_points = []
# for i in range(defects.shape[0]):
#     s, e, f, d = defects[i, 0]
#     if d > depth_threshold:
#         defect_points.append((f, d))  # f：缺陷最凹点索引

# if len(defect_points) < 2:
#     print("检测到的有效凸性缺陷不足，无法分割轮廓")
#     exit()

# # 按缺陷深度降序排序，选择最深的两个缺陷点
# defect_points = sorted(defect_points, key=lambda x: x[1], reverse=True)
# split_idx1, d1 = defect_points[0]
# split_idx2, d2 = defect_points[1]

# # 保证顺序：较小的索引在前
# if split_idx1 > split_idx2:
#     split_idx1, split_idx2 = split_idx2, split_idx1

# # 在原图上标记这两个缺陷点（便于调试）
# img_defects = img_show.copy()
# cv2.circle(img_defects, tuple(contour[split_idx1][0]), 5, (0, 0, 255), -1)
# cv2.circle(img_defects, tuple(contour[split_idx2][0]), 5, (0, 0, 255), -1)
# cv2.imshow("Defect Points", img_defects)
# cv2.waitKey(0)

# # 5. 分割轮廓为两部分
# # 将 contour 转换为二维数组，便于切分（squeeze 掉冗余维度）
# contour_pts = contour.squeeze()  # 形状应为 (N, 2)
# if len(contour_pts.shape) != 2:
#     print("轮廓点维度异常")
#     exit()

# # 第一部分：从 split_idx1 到 split_idx2（包含两端）
# part1 = contour_pts[split_idx1:split_idx2+1]
# # 第二部分：从 split_idx2 到末尾，再从起点到 split_idx1（拼接起来）
# part2 = np.concatenate((contour_pts[split_idx2:], contour_pts[:split_idx1+1]), axis=0)

# # 可视化分割后的两个部分
# img_parts = img_show.copy()
# cv2.drawContours(img_parts, [part1.reshape(-1,1,2)], -1, (255, 0, 0), 2)  # 蓝色
# cv2.drawContours(img_parts, [part2.reshape(-1,1,2)], -1, (0, 255, 255), 2)  # 黄色
# cv2.imshow("Split Contour Parts", img_parts)
# cv2.waitKey(0)

# # 6. 对每个部分拟合椭圆（需要至少 5 个点）
# # 读取一张 RGB 图用于显示拟合效果（若无，可使用彩色化的 mask）
# rgb_img = cv2.imread('tree_rgb.jpg')
# if rgb_img is None:
#     rgb_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

# if part1.shape[0] >= 5:
#     ellipse1 = cv2.fitEllipse(part1.reshape(-1,1,2))
#     cv2.ellipse(rgb_img, ellipse1, (0, 0, 255), 2)  # 红色椭圆
# else:
#     print("第一部分点数不足，无法拟合椭圆")

# if part2.shape[0] >= 5:
#     ellipse2 = cv2.fitEllipse(part2.reshape(-1,1,2))
#     cv2.ellipse(rgb_img, ellipse2, (255, 0, 0), 2)  # 蓝色椭圆
# else:
#     print("第二部分点数不足，无法拟合椭圆")

# cv2.imshow("Ellipses from Split Contour", rgb_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()