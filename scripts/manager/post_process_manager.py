# process_manager.py
import os
import json
import time
import random

from process.density_classfication import DensityClassification
from process.fruit_count import FruitCount
from process.height_calc import HeightCalculate
from process.tree_count import TreeNumberCount
from save.save2sql import ImageDataDB
class PostProcessManager:
    def __init__(self, root_data_path, localization_file, options, device_id):
        """
        :param root_data_path: 数据存放的根目录路径，根目录下包含多个采集会话文件夹，
                                每个会话文件夹中包含 rgb 和 depth 子目录以及 image.json 文件
        :param localization_file: 定位信息 JSON 文件路径，文件中存放多个定位记录
        :param options: 字典，指示选中哪些处理任务，例如
                        {"density": True, "height": True, "fruit count": False, "treenumber": True}
        :param device_id: 当前设备ID，用于记录在结果 JSON 中
        """
        self.root_data_path    = root_data_path
        self.localization_file = localization_file
        self.options           = options
        self.device_id         = device_id

        # 初始化各个处理类
        self.density_classifier = DensityClassification()
        self.fruit_counter      = FruitCount()
        self.height_calculator  = HeightCalculate()
        self.tree_counter       = TreeNumberCount()

        # 加载定位数据（假设定位 JSON 文件中存放的是一个列表）
        self.localization_data = self._load_localization_data()

    def _load_localization_data(self):
        if not os.path.exists(self.localization_file):
            print(f"Localization file {self.localization_file} not found.")
            return []
        with open(self.localization_file, 'r') as f:
            data = json.load(f)
        return data

    def _find_closest_localization(self, target_timestamp):
        """在定位数据中查找与 target_timestamp 最接近的一条记录"""
        if not self.localization_data:
            return None
        closest_entry = None
        min_diff = float('inf')
        for entry in self.localization_data:
            # 假设每条定位记录中有 "timestamp" 字段（单位为秒）
            diff = abs(entry["timestamp"] - target_timestamp)
            if diff < min_diff:
                min_diff = diff
                closest_entry = entry
        return closest_entry

    def process_all(self, output_file="final_result.json"):
        """
        遍历 root_data_path 下的每个采集会话文件夹，处理数据并保存结果到 JSON 文件中。
        每个会话文件夹要求包含 rgb 和 depth 子目录，以及 image.json 文件（其中包含采集时的 timestamp）。
        返回结果格式为一个列表，每个元素格式如下：
        {
            "timestamp": timestamp,
            "rgb_path": rgb_path,
            "depth_path": depth_path,
            "device_id": device_id,
            "result": {
                "density": ...,
                "height": ...,
                "fruit_count": ...,
                "tree_id": ...
            },
            "latitude": ...,
            "longitude": ...,
            "altitude": ...
        }
        """
        all_results = []
        # 遍历 root_data_path 下的所有子目录（每个目录代表一个采集会话）
        for session in os.listdir(self.root_data_path):
            session_path = os.path.join(self.root_data_path, session)
            if not os.path.isdir(session_path):
                continue

            # 检查是否存在 rgb 和 depth 子目录
            rgb_dir   = os.path.join(session_path, "rgb")
            depth_dir = os.path.join(session_path, "depth")
            if not (os.path.exists(rgb_dir) and os.path.exists(depth_dir)):
                print(f"Skipping {session_path}: missing rgb or depth folder.")
                continue

            # 读取 image.json 获取采集时间戳（如果不存在则使用当前时间）
            image_json_path = os.path.join(session_path, "image.json")
            if os.path.exists(image_json_path):
                try:
                    with open(image_json_path, 'r') as f:
                        image_info = json.load(f)
                    timestamp = image_info.get("timestamp", time.time())
                except Exception as e:
                    print(f"Error reading {image_json_path}: {e}")
                    timestamp = time.time()
            else:
                timestamp = time.time()

            results = {}
            # 根据选项调用各个处理类
            if self.options.get("density", False):
                # 假设 DensityClassification 的 process 方法接收当前会话的路径
                density_obj = self.density_classifier.process(session_path)
                results["density"] = density_obj.process()
            if self.options.get("height", False):
                height_obj = self.height_calculator.process(session_path)
                results["height"] = height_obj.process()
            if self.options.get("fruit count", False):
                fruit_obj = self.fruit_counter.process(session_path)
                results["fruit_count"] = fruit_obj.process()
            if self.options.get("treenumber", False):
                tree_obj = self.tree_counter.process(session_path)
                results["tree_id"] = tree_obj.process()

            # 将 rgb 和 depth 的路径添加到结果中
            result_entry = {
                "timestamp": timestamp,
                "rgb_path": rgb_dir,
                "depth_path": depth_dir,
                "device_id": self.device_id,
                "result": results
            }

            # 查找与该 timestamp 最接近的定位记录，并添加其定位信息
            loc = self._find_closest_localization(timestamp)
            if loc:
                result_entry["latitude"]  = loc.get("latitude")
                result_entry["longitude"] = loc.get("longitude")
                result_entry["altitude"]  = loc.get("altitude")
            else:
                result_entry["latitude"]  = None
                result_entry["longitude"] = None
                result_entry["altitude"]  = None

            all_results.append(result_entry)

        # 保存所有结果到 JSON 文件
        try:
            with open(output_file, "w") as f:
                json.dump(all_results, f, indent=4)
            print(f"Processing results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results to JSON: {e}")
        return all_results

    def save2database(self, db_path="data/analysis.db", json_file="final_result.json"):

        
        db = ImageDataDB(db_path)
        # 这里假设 JSON 文件中存储的是一个列表，每个元素包含定位信息
        if not os.path.exists(json_file):
            print(f"JSON file {json_file} does not exist!")
            return
        with open(json_file, "r") as f:
            data = json.load(f)
            for entry in data:
                # 数据库表结构中要求的字段：timestamp, rgb_path, depth_path, latitude, longitude, altitude
                db.insert_data(entry)
        db.close()
        print("All results saved to database.")

# 示例调用
if __name__ == '__main__':
    # 假设从 UI 中获得以下信息
    import os
    root_data_path    = os.path.expanduser("~/Documents/Agrosense/data/images")
    localization_file = os.path.expanduser("~/Documents/Agrosense/data/localization.json")
    options = {
        "density": True,
        "height": True,
        "fruit count": True,
        "treenumber": True
    }
    device_id = "cam1"
    manager = PostProcessManager(root_data_path, localization_file, options, device_id)
    # 处理所有采集会话，并保存结果到 final_result.json
    manager.process_all("final_result.json")
    # 将最终结果写入数据库
    manager.save2database("data/analysis.db", "final_result.json")
