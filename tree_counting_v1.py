from ultralytics import YOLO
from pathlib import Path
import os
import glob
import numpy as np
import cv2
import pandas as pd


def yolo_detection(image_path: str, weights: str = "train3/weights/best.pt",
                   project: str = "runs/detect", name: str = "predict5",
                   iou: float = 0.1):

    model = YOLO(weights)

    results = model(
        image_path,
        stream=True,
        save=True,
        save_txt=True,
        save_conf=True,
        iou=iou,
        project=project,
        name=name,
        exist_ok=True
    )

    for _ in results:
        break

    # 构造标签文件的路径
    img_stem = Path(image_path).stem
    label_dir = Path(project) / name / "labels"
    label_path = label_dir / f"{img_stem}.txt"

    if not label_path.exists():  # 如果没有检测出物体，就不会自己生成txt文件，需要自己补齐一个
        label_dir.mkdir(parents=True, exist_ok=True)  # 确保标签目录存在
        label_path.write_text("")  # 创建空 txt 文件

    return str(label_path)


def filter_label_file(label_path: str, threshold_norm: float = 0.3, area_threshold: float = 0.005):
    """
    作用是去掉不相关的bounding box
    读取并过滤一个 YOLO label 文件（每行：
      class x_center y_center width height [confidence]
    归一化到 0~1）。只保留符合“最左侧 + buffer + 最高置信度”规则的那一行。
    返回：保留的那一行（含 '\n'），或空列表（文件无内容）。
    """
    # 读所有行

    arr = np.loadtxt(label_path, ndmin=2)  # 确保返回 shape==(1,6) 或 (N,6)

    if arr.size == 0:
        return []

        # x_center 在第 1 列，conf 在第 5 列
    x_centers = arr[:, 1]
    y_centers = arr[:, 2]
    w = arr[:, 3]
    h = arr[:, 4]
    areas = w * h


    # 然后在同一个 mask 里同时加上 x_center 和 面积 的阈值：bbx 太小的不要，xcenter太大说明bbx不在地上，可能是树枝上的，也去掉
    mask = (x_centers < threshold_norm) & (areas >= area_threshold)
    candidates = arr[mask]

    # 如果没有符合条件的，就全都返回
    if len(candidates) == 0:
        return []
    elif len(candidates) == 1:  # 如果只有一个就不用管了
        return candidates
    else:  # 如果还是有多个，就要保证同一水平线上（垂直于地面方向）只有一个bbx
        xc = candidates[:, 1]
        yc = candidates[:, 2]
        y_threshold = 0.15
        keep = np.ones(candidates.shape[0], dtype=bool)

        for i in range(len(keep)):
            if not keep[i]:
                continue
            for j in range(i+1, len(keep)):
                if not keep[j]:
                    continue
                if abs(yc[i] - yc[j]) < y_threshold:
                    # 同水平线，删掉 x 更大的 （更高的）
                    if xc[i] < xc[j]:
                        keep[j] = False
                    else:
                        keep[i] = False
                        break

        candidates = candidates[keep]  # 肯定是大于等于1的

        # 4) 返回过滤后的子集
        return candidates


def nonblack_ratio(image_path, x, y, w, h):   # y central 默认197
    # 提取 图片中间部分的ROI
    img = cv2.imread(image_path)
    roi = img[y:y+h, x:x+w]

    # 判断黑色像素
    is_black = np.all(roi == [0, 0, 0], axis=-1)
    black_pixels = int(np.sum(is_black))
    color_pixels = int(roi.shape[0] * roi.shape[1] - black_pixels)
    ratio = color_pixels / (roi.shape[0] * roi.shape[1])

    return ratio



def ratio_select_filter(image_path: str, candidates, ratio_threds):
    filtered_box = []
    if len(candidates) == 0:
        return np.array(filtered_box)
    else:
        for i in range(len(candidates)):
            y = candidates[i, 2]
            H = cv2.imread(image_path).shape[0]  # 图像高度
            y_pixel = int(y * H)
            nonblack_ratio_box = nonblack_ratio(image_path, x = 92, y = y_pixel, w = 177, h = 65)
            # print("filtered nonblack ratio ", nonblack_ratio_box)
            if nonblack_ratio_box > ratio_threds:
                filtered_box.append(candidates[i])
    return np.array(filtered_box)


def get_central(list):
    mid_index = len(list) // 2
    middle_element = list[mid_index]
    return middle_element






if __name__ == '__main__':

    # # Define path to directory containing images and videos for inference
    # source = "014/left/filtered_data_L14-55/0000245.png"

    # txt_path = yolo_detection(source)
    # print("标签文件保存在：", txt_path)

    # selectboxs = filter_label_file(txt_path)
    # print("final selected boxes:",selectboxs)

    # nonblack_ratio_result = nonblack_ratio(source)
    # print(nonblack_ratio_result)

    image_dir = "014/left/filtered_data_L14-55"
    out_dir   = "detected_trunks"
    os.makedirs(out_dir, exist_ok=True)

    # 1. 按数字 filename 排序
    paths = glob.glob(os.path.join(image_dir, "*.png"))
    paths = sorted(paths, key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))



    # 2. 预计算 y_centers 和 ratios。ycenter因该是从大到小的，因为树是从图片的下方移动到上方
    y_centers = []
    ratios    = []
    save_result = []
    activetrack = []
    y_gap = 0.2 

    for p in paths:  # p 就是对应的文件名
        txt  = yolo_detection(p)
        line = filter_label_file(txt)
        # print("line ", line)
        filtered_line = ratio_select_filter(p, line, ratio_threds = 0.2)
        # print("filtered line type:", type(filtered_line))
        # print("filtered line content:", filtered_line)
        # print("y_center", filtered_line[:,2])
        # print("filtered line.shape:", getattr(line, "shape", "no shape"))


        if isinstance(filtered_line, np.ndarray) and filtered_line.shape[0] == 1:
            y_vals = filtered_line[:, 2]  # 第3列是 y_center
            y_centers.append(y_vals.tolist())  

        elif isinstance(filtered_line, np.ndarray) and filtered_line.shape[0] > 1:  # 如果不是只有一个，查看上一个图片保留的y，在这个图片上保留小于上一个y最近的那个值
            y_last = y_centers[-1]
            y_vals = filtered_line[:, 2]  # 第3列是 y_center

            if len(y_last) != 0:
                # 1. 过滤出所有小于 y_last 的 y_vals
                valid_indices = np.where(y_vals < y_last)[0]

                if len(valid_indices) > 0:
                    # 2. 在这些里面找距离 y_last 最近的一个（最大的小于 y_last 的）
                    closest_index = valid_indices[np.argmin(np.abs(y_vals[valid_indices] - y_last))]
                    selected_y = y_vals[closest_index]
                else:
                    # 3. 如果没有比 y_last 小的，就取最大的 y_center。这里有待考量！！！
                    selected_y = np.max(y_vals)
                y_centers.append([float(selected_y)]) 
            else: # 前面一个列表正好是空的情况，直接留下y最大的那个，因为新的树都是要从最大的进去的
                selected_y = np.max(y_vals)
                y_centers.append([float(selected_y)]) 
        else:
            y_centers.append([])
        # print("y centers list:", y_centers)
        ratios.append(nonblack_ratio(p, x = 92, y = 197, w = 177, h = 65))
        # print("ratios:", ratios)


        y_last = next((yc[0] for yc in reversed(y_centers[:-1]) if yc), None)


        print("y last", y_last)
        print("ycenteral last", y_centers[-1])


        if y_centers[-1] != [] and y_last != None:   # y centers -1 一定要比 y last小的
            # if y_centers[-1][0]  



            if abs(y_centers[-1][0] - y_last) < y_gap: 
                print("the same tree")
                activetrack.append((y_centers[-1], p, ratios[-1]))  # 保存本此处理的ycenter和文件名
                print("activate track list", activetrack)

            else:   # 最后一个元素不是空，并且比前面最近的那个元素之间距离大于gap，表示是一个新的树出现了
                print("it is a new tree")

                valid_track = [x for x in activetrack if x[0] and isinstance(x[0], list)]
                if valid_track:
                    middle = min(valid_track, key=lambda x: abs(x[0][0] - 0.5))  # 这里选择保存的树只用了y central， 没有使用nonblack ratio
                    print("最靠近中心的帧是：", middle)

                if len(valid_track)>= 5:
                    save_result.append(middle)  # 先保存文件名
                    print("valid, saved in result")

                print("gap works, the previous tree middle is", middle)
                print("current activetrack is:", activetrack)
                activetrack = []
                activetrack.append((y_centers[-1], p, ratios[-1]))  # 保存本此处理的ycenter和文件名
                print("the new activetrack is", activetrack)


        elif y_centers[-1] != [] and y_last == None:  # 表示是第一个有值的元素， 认为序列刚开始
            print("a new tree just start")
            activetrack.append((y_centers[-1], p, ratios[-1]))  # 保存本此处理的ycenter和文件名

        elif y_centers[-1] == []:
            # 表示直接进入下一个， 其实不需要计算y last了
            activetrack.append((y_centers[-1], p, ratios[-1]))  

    if activetrack != 0:
        print("the last one")
        valid_track = [x for x in activetrack if x[0] and isinstance(x[0], list)]
        if valid_track:
            middle = min(valid_track, key=lambda x: abs(x[0][0] - 0.5))  # 这里选择保存的树只用了y central， 没有使用nonblack ratio
            print("最靠近中心的帧是：", middle)

        if len(valid_track)>= 5:
            save_result.append(middle)  # 先保存文件名
            print("valid, saved in result")
        activetrack = []

    print(save_result)




























