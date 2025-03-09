
import sqlite3
import json
import os

class DataProcessor:
    def __init__(self, db_path="data/combined_data.db"):
        """
        初始化 SQLite 数据库连接，并创建表（如果尚未创建）。
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        创建数据库表，用于存储图像和 GPS 的组合数据。
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_timestamp TEXT,
            rgb_path TEXT,
            depth_path TEXT,
            gps_timestamp TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            device_id TEXT
        )
        ''')
        self.conn.commit()

    def insert_data(self, combined_entry):
        """
        插入一条组合后的数据到数据库。
        """
        self.cursor.execute('''
        INSERT INTO combined_data (
            image_timestamp, rgb_path, depth_path, gps_timestamp,
            latitude, longitude, altitude, device_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            combined_entry["image_timestamp"],
            combined_entry["rgb_path"],
            combined_entry["depth_path"],
            combined_entry["gps_timestamp"],
            combined_entry["latitude"],
            combined_entry["longitude"],
            combined_entry["altitude"],
            combined_entry["device_id"]
        ))
        self.conn.commit()

    def close(self):
        """关闭数据库连接。"""
        self.conn.close()

def combine_and_save_data(image_dir, gps_dir, db_processor):
    """
    读取图像 JSON 和 GPS JSON 数据，按规则匹配后保存到数据库中。
    
    :param image_dir: 图像 JSON 文件所在目录
    :param gps_dir: GPS JSON 文件所在目录
    :param db_processor: 数据库处理对象
    """
    # 获取所有 JSON 文件
    image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".json")])
    gps_files = sorted([os.path.join(gps_dir, f) for f in os.listdir(gps_dir) if f.endswith(".json")])

    gps_data = []
    # 加载所有 GPS 数据
    for gps_file in gps_files:
        with open(gps_file, "r") as f:
            gps_data.extend(json.load(f))

    # 加载图像数据并进行组合
    for image_file in image_files:
        with open(image_file, "r") as f:
            image_data = json.load(f)
        
        for idx, img_entry in enumerate(image_data):
            gps_idx = (idx + 1) * 10 - 1  # 图像第 n 个对应 GPS 第 n*10 个 (索引从 0 开始，所以减 1)
            if gps_idx < len(gps_data):
                gps_entry = gps_data[gps_idx]
                # 合并图像和 GPS 信息
                combined_entry = {
                    "image_timestamp": img_entry["timestamp"],
                    "rgb_path": img_entry["rgb_path"],
                    "depth_path": img_entry["depth_path"],
                    "gps_timestamp": gps_entry["timestamp"],
                    "latitude": gps_entry["latitude"],
                    "longitude": gps_entry["longitude"],
                    "altitude": gps_entry["altitude"],
                    "device_id": img_entry["device_id"]
                }
                # 保存到数据库
                db_processor.insert_data(combined_entry)
            else:
                print(f"Skipping: No GPS data for image index {idx + 1}")

# 使用示例
if __name__ == "__main__":
    # 图像和 GPS 数据目录
    image_dir = "data/033422071163"
    gps_dir = "data/033422071163/gps"

    # 创建数据库处理对象
    db_processor = DataProcessor()

    # 组合并保存数据
    combine_and_save_data(image_dir=image_dir, gps_dir=gps_dir, db_processor=db_processor)

    # 关闭数据库连接
    db_processor.close()
