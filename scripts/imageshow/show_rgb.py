# imageshow_rgb.py
import pyrealsense2 as rs
import numpy as np
import cv2
from PyQt5.QtGui import QImage

def start_rgb_stream(device_id, width, height, fps, exposure, gain, image_callback):
    """
    启动 RGB 图像采集，仅采集彩色图像。
    
    :param device_id: 相机设备ID
    :param width: 图像宽度
    :param height: 图像高度
    :param fps: 帧率
    :param exposure: 曝光参数
    :param gain: 增益参数
    :param image_callback: 回调函数，格式为 image_callback(device_id, QImage)
    """
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(device_id)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
    profile = pipeline.start(config)
    
    # 设置相机参数（注意不同设备的传感器顺序可能不同，这里简单遍历所有传感器尝试设置）
    sensors = profile.get_device().query_sensors()
    for sensor in sensors:
        try:
            sensor.set_option(rs.option.enable_auto_exposure, False)
            sensor.set_option(rs.option.exposure, exposure)
            sensor.set_option(rs.option.gain, gain)
        except Exception as e:
            # 如果当前传感器不支持，则忽略
            print(f"设备 {device_id} 设置参数失败：{e}")

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            # 将彩色帧转换为 numpy 数组（BGR格式）
            color_image = np.asanyarray(color_frame.get_data())
            # 将 BGR 转为 RGB（QImage 要求 RGB 顺序）
            rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # 通过回调函数传递图像数据
            image_callback(device_id, qimg)
            # 等待1毫秒，防止占用过多CPU
            cv2.waitKey(1)
    except Exception as e:
        print(f"设备 {device_id} 采集出错：{e}")
    finally:
        pipeline.stop()
