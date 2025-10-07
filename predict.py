from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("train3/weights/best.pt")

# Define path to directory containing images and videos for inference
source = "014/left/filtered_data_L14-55" 


# Run inference on the source
results = model(source, stream=True, save=True, save_frames=True, save_txt=True, save_conf=True, iou=0.1)  # generator of Results objects iou default 0.7
for result in results:
    print(result)  # 这样可以查看每个推理结果

# iou 足够小，让输出的label很少有重叠
