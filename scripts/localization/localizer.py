import time
from queue import Empty

class Localizer:
    """
    Localizer 类负责从共享队列中读取高频传感器数据（GPS、IMU等），
    并进行数据融合计算，得到最终的定位结果。
    
    融合后的结果会更新到共享数据字典 shared_data 中，键包括：
      - "lat"：纬度
      - "Lon"：经度
      - "velocity"：速度
      - "acc"：加速度
    """
    def __init__(self, shared_queue, shared_data):
        """
        :param shared_queue: 用于从通信模块接收数据的共享队列
        :param shared_data: 用于存放融合结果的共享字典（例如 multiprocessing.Manager().dict()）
        """
        self.shared_queue = shared_queue
        self.shared_data = shared_data
        self.latest_gps = None
        self.latest_imu = None

    def run(self):
        """不断从共享队列中读取数据并进行融合计算"""
        while True:
            try:
                data = self.shared_queue.get(timeout=1)
                self.process_data(data)
            except Empty:
                continue

    def process_data(self, data):
        """
        根据数据类型更新内部状态，然后进行简单融合：
          - 收到GPS数据时，更新最新的经纬度信息
          - 收到IMU数据时，更新最新的速度和加速度
          
        当同时拥有GPS和IMU数据时，认为位置以GPS为准，速度和加速度以IMU为准，
        并将结果更新到 shared_data 字典中，键为 "lat"、"Lon"、"velocity" 和 "acc"。
        """
        if data["type"] == "gps":
            self.latest_gps = data
        elif data["type"] == "imu":
            self.latest_imu = data

        # 当同时收到GPS和IMU数据时，进行融合计算
        if self.latest_gps is not None and self.latest_imu is not None:
            fused_lat = self.latest_gps["lat"]
            fused_lon = self.latest_gps["lon"]
            fused_velocity = self.latest_imu["velocity"]
            fused_acceleration = self.latest_imu["acceleration"]

            # 更新共享数据
            self.shared_data["lat"] = fused_lat
            self.shared_data["Lon"] = fused_lon
            self.shared_data["velocity"] = fused_velocity
            self.shared_data["acc"] = fused_acceleration

            print(f"Fused data updated: lat={fused_lat}, Lon={fused_lon}, "
                  f"velocity={fused_velocity}, acc={fused_acceleration}")
