import os
import json
from datetime import datetime
import random

def generate_gps_data_and_save(batch_size=100, total_data=1000, device_id="033422071163"):
    """
    自动生成 GPS 数据，并按 batch_size 条数据保存到一个 JSON 文件。
    
    :param batch_size: 每批保存到 JSON 文件的条数
    :param total_data: 需要生成的总数据量
    :param device_id: 设备 ID，用于标识数据来源
    """
    # 创建存储目录
    base_dir = f"data/{device_id}/gps"
    os.makedirs(base_dir, exist_ok=True)

    # 初始化计数器和数据列表
    gps_data_list = []
    file_index = 0

    # 模拟生成 GPS 数据的循环
    for i in range(1, total_data + 1):
        # 获取当前时间戳
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 模拟生成随机 GPS 数据
        latitude = random.uniform(30.0, 31.0)  # 随机生成纬度
        longitude = random.uniform(120.0, 121.0)  # 随机生成经度
        altitude = random.uniform(10.0, 100.0)  # 随机生成海拔

        # 模拟 GPS 数据条目
        gps_data = {
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "device_id": device_id
        }
        gps_data_list.append(gps_data)

        # 每 batch_size 条保存到一个 JSON 文件
        if len(gps_data_list) == batch_size:
            json_file = f"{base_dir}/gps_data_{file_index:04}.json"
            with open(json_file, "w") as f:
                json.dump(gps_data_list, f, indent=4)
            print(f"Saved {json_file} with {batch_size} entries.")
            
            # 重置数据列表并更新文件索引
            gps_data_list = []
            file_index += 1

    # 如果还有剩余数据，保存最后一个 JSON 文件
    if gps_data_list:
        json_file = f"{base_dir}/gps_data_{file_index:04}.json"
        with open(json_file, "w") as f:
            json.dump(gps_data_list, f, indent=4)
        print(f"Saved {json_file} with {len(gps_data_list)} entries.")

# 调用函数生成数据
generate_gps_data_and_save(batch_size=100, total_data=1000, device_id="033422071163")
