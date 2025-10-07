import os
import json

# 自定义类别名称列表（请修改为你的类别）
CLASS_NAMES = ["trunk"]  # 请按照你的类别修改

def convert_labelme_to_yolo(json_folder, output_folder, class_names):
    """
    将 LabelMe JSON 转换为 YOLO 格式的 TXT
    :param json_folder: 存放 LabelMe JSON 文件的目录
    :param output_folder: 存放转换后的 YOLO TXT 标签文件的目录
    :param class_names: 类别名称列表（用于映射 class_id）
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for json_file in os.listdir(json_folder):
        if not json_file.endswith(".json"):
            continue

        json_path = os.path.join(json_folder, json_file)
        txt_path = os.path.join(output_folder, json_file.replace(".json", ".txt"))

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_width = data["imageWidth"]
        image_height = data["imageHeight"]
        shapes = data["shapes"]

        with open(txt_path, "w", encoding="utf-8") as f:
            for shape in shapes:
                label = shape["label"]
                if label not in class_names:
                    print(f"警告: {label} 不在类别列表中，跳过该对象")
                    continue

                class_id = class_names.index(label)
                points = shape["points"]
                x_min, y_min = points[0]
                x_max, y_max = points[1]

                # 计算归一化 YOLO 格式
                x_center = ((x_min + x_max) / 2) / image_width
                y_center = ((y_min + y_max) / 2) / image_height
                width = (x_max - x_min) / image_width
                height = (y_max - y_min) / image_height

                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"转换完成: {json_file} -> {txt_path}")

# 设置 JSON 目录和 YOLO 标签输出目录
json_folder = "train_L13_labels"  # LabelMe JSON 文件目录
output_folder = "yoloL13_labels"  # YOLO 格式 TXT 输出目录

convert_labelme_to_yolo(json_folder, output_folder, CLASS_NAMES)
