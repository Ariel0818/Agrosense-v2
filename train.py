from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("train2_best.pt")

# Train the model on the COCO8 example dataset for 150 epochs
results = model.train(data="data.yaml", epochs=150, imgsz=640)