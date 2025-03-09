# json_saver.py
import json
import os

def save_image2json(timestamp, rgb_path, depth_path, device_id, output_file="image_data.json"):
    """
    将图像数据保存为 JSON 格式：
    {
        "timestamp": timestamp,
        "rgb_path": rgb_path,
        "depth_path": depth_path,
        "device_id": device_id
    }
    """
    data = {
        "timestamp": timestamp,
        "rgb_path": rgb_path,
        "depth_path": depth_path,
        "device_id": device_id
    }
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Image data saved to {output_file}")
    except Exception as e:
        print(f"Error saving image JSON: {e}")

def save_localization2json(timestamp, latitude, longitude, altitude, output_file="localization_data.json"):
    """
    将定位数据保存为 JSON 格式：
    {
        "timestamp": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude 
    }
    """
    gps_data = {
        "timestamp": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude
    }
    try:
        with open(output_file, "w") as f:
            json.dump(gps_data, f, indent=4)
        print(f"Localization data saved to {output_file}")
    except Exception as e:
        print(f"Error saving localization JSON: {e}")
