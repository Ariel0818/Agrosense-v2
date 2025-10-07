from pathlib import Path
from ultralytics import YOLO

def yolo_detection(image_path: str,
                   weights: str = "train3/weights/best.pt",
                   project: str = "runs/detect",
                   name: str = "predict5",
                   iou: float = 0.1):
    """
    在 runs/detect/<name>/labels/ 目录下保存 txt 标签，并返回标签文件的绝对路径。
    """
    # 1. 加载模型
    model = YOLO(weights)
    
    # 2. 推理并保存结果（含 txt 标签）
    #    stream=True 会返回一个生成器，内部会在每一次迭代时保存对应的文件
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

    # 3. 迭代一次，以确保触发保存
    #    同时，我们只处理单张图时，立即取出第一个结果
    for _ in results:
        break

    # 4. 构造标签文件的路径
    img_stem = Path(image_path).stem
    label_dir = Path(project) / name / "labels"
    label_path = label_dir / f"{img_stem}.txt"

    # 5. 返回
    return str(label_path)

# 调用示例
if __name__ == "__main__":
    txt_path = yolo_detection("014/left/filtered_data_L14-55/0001078.png")
    print("标签文件保存在：", txt_path)
