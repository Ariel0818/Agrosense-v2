import cv2
import numpy as np

# 定义可视化函数
def visualize(image_path, label_path, class_names):
    # 读取图片
    image = cv2.imread(image_path)

    # 获取图片的大小
    height, width, _ = image.shape

    # 读取标签文件
    with open(label_path, "r") as f:
        lines = f.readlines()

    # 遍历每个标签
    for line in lines:
        # 解析标签
        class_id, x, y, w, h = map(float, line.split())
        class_name = class_names[int(class_id)]

        # 计算 bounding box 的坐标
        left = int((x - w / 2) * width)
        top = int((y - h / 2) * height)
        right = int((x + w / 2) * width)
        bottom = int((y + h / 2) * height)

        # 绘制 bounding box
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

        # 绘制类别名称
        text_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.putText(image, class_name, (left, top - text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 显示图片
    cv2.imshow("visualization", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    visualize(r"train_L13/0000116.png", r"yoloL13_labels/0000116.txt", ["trunk"])

