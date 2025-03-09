import os
import json
import time
from datetime import datetime

def generate_data_and_save(batch_size=10, total_data=100, device_id="033422071163"):
    """
    自动生成图像路径信息，并每 batch_size 条数据保存到一个 JSON 文件。
    
    :param batch_size: 每批保存到 JSON 文件的条数
    :param total_data: 需要生成的总数据量
    :param device_id: 设备 ID，用于生成路径
    """
    # 创建存储路径
    base_dir = f"data/{device_id}"
    rgb_dir = f"{base_dir}/rgb"
    depth_dir = f"{base_dir}/depth"
    os.makedirs(rgb_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

    # 初始化计数器和数据列表
    data_list = []
    file_index = 0

    # 模拟数据生成循环
    for i in range(1, total_data + 1):
        # 获取当前时间戳
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # 构造 RGB 和深度图像路径
        rgb_path = f"{rgb_dir}/image_{timestamp.replace(':', '').replace('-', '')}_{i:06}.png"
        depth_path = f"{depth_dir}/depth_{timestamp.replace(':', '').replace('-', '')}_{i:06}.png"

        # 模拟数据条目
        data = {
            "timestamp": timestamp,
            "rgb_path": rgb_path,
            "depth_path": depth_path,
            "device_id": device_id
        }
        data_list.append(data)

        # 每 batch_size 条保存到一个 JSON 文件
        if len(data_list) == batch_size:
            json_file = f"{base_dir}/metadata_{file_index:04}.json"
            with open(json_file, "w") as f:
                json.dump(data_list, f, indent=4)
            print(f"Saved {json_file} with {batch_size} entries.")
            
            # 重置数据列表并更新文件索引
            data_list = []
            file_index += 1

    # 如果还有剩余数据，保存最后一个 JSON 文件
    if data_list:
        json_file = f"{base_dir}/metadata_{file_index:04}.json"
        with open(json_file, "w") as f:
            json.dump(data_list, f, indent=4)
        print(f"Saved {json_file} with {len(data_list)} entries.")

# 调用函数生成数据
generate_data_and_save(batch_size=10, total_data=100, device_id="033422071163")
