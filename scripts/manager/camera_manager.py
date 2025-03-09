# camera_manager.py
import pyrealsense2 as rs
import numpy as np
import cv2
from utils.log import LoggerManager

logger_manager = LoggerManager()
logger = logger_manager.get_logger()

from dataCollection.data_collect import SingleCamera  # 假设 SingleCamera 定义在 dataCollect.py 中

class CameraManager:
    def __init__(self, device_ids, exposure, gain, width=640, height=480, fps=30):
        """
        初始化多个相机, device_ids 是一个包含所有相机设备 ID 的列表
        """
        self.cameras = {}
        for device in device_ids:
            try:
                cam = SingleCamera(device, exposure, gain, width, height, fps)
                self.cameras[device] = cam
                logger.info(f"CameraManager: Camera {device} initialized.")
            except Exception as e:
                logger.error(f"CameraManager: Failed to initialize camera {device}: {e}")

    def show_camera_image(self, device_id, stop_event):
        """
        调用指定相机的 showImage 方法显示实时图像
        """
        if device_id in self.cameras:
            logger.info(f"CameraManager: Showing image for camera {device_id}.")
            self.cameras[device_id].showImage(stop_event)
        else:
            logger.error(f"CameraManager: Camera {device_id} not found.")

    def update_camera_parameters(self, device_id, new_exposure, new_gain):
        """
        更新指定相机的参数：曝光和增益
        """
        if device_id in self.cameras:
            cam          = self.cameras[device_id]
            cam.exposure = new_exposure
            cam.gain     = new_gain
            try:
                cam.sensor.set_option(rs.option.exposure, new_exposure)
                cam.sensor.set_option(rs.option.gain, new_gain)
                logger.info(f"CameraManager: Updated camera {device_id}: exposure={new_exposure}, gain={new_gain}")
            except Exception as e:
                logger.error(f"CameraManager: Failed to update camera {device_id}: {e}")
        else:
            logger.error(f"CameraManager: Camera {device_id} not found.")
