# data_collect_manager.py
import time
from save.save2json import save_image2json, save_localization2json

class RealTimeProcessManager:
    def __init__(self, camera_manager, navigator, localizer):
        """
        :param data_collect: 负责采集数据的类对象（例如 SingleCamera 的管理或其他采集类）
        :param navigator: 负责与下位机通信，获取 GPS/IMU 数据的类对象（例如 USB2Navigator）
        :param localizer: 负责计算位置信息的类对象（例如 Localizer 类）
        """
        self.cameraMananger = camera_manager
        self.navigator    = navigator
        self.localizer    = localizer

    def start(self):
        """
        启动任务管理：
         - 启动下位机通信（GPS、IMU）
         - 启动数据采集任务
         - 定时获取数据、计算位置信息并保存到 JSON 文件中
        """
        # 启动下位机通信
        self.navigator.send_start_signal()
        print("Navigator started, start signal sent.")

        # 启动数据采集任务（假设 data_collect 内部实现了采集线程或进程）
        self.data_collect.start_collecting()
        print("Data collection started.")

        try:
            while True:
                # 获取当前时间戳
                timestamp = time.time()

                # 获取GPS/IMU数据
                # 此处假设 receive_data() 方法会更新 navigator 内部的 gps 数据
                self.navigator.receive_data()

                # 计算当前定位信息
                # 这里你可以调用 localizer 中的算法，示例中直接使用 navigator 的数据
                latitude = self.navigator.position_lat
                longitude = self.navigator.position_lon
                altitude = 0.0  # 若有 altitude 信息，请从 localizer 或其他传感器中获取

                # 保存定位数据到 JSON 文件
                save_localization2json(timestamp, latitude, longitude, altitude)

                # 获取采集的数据（假设 data_collect 提供 get_data() 方法返回字典格式数据）
                collected_data = self.cameraMananger.get_data()
                if collected_data:
                    rgb_path = collected_data.get("rgb_path")
                    depth_path = collected_data.get("depth_path")
                    device_id = collected_data.get("device_id")
                    # 保存图像数据到 JSON 文件
                    save_image2json(timestamp, rgb_path, depth_path, device_id)
                else:
                    print("No collected data available at this cycle.")

                # 休眠一段时间，周期性采集保存（具体周期可根据需要调整）
                time.sleep(1)
        except KeyboardInterrupt:
            print("Data collection interrupted by user.")
        finally:
            # 停止任务时，可发送停止信号
            self.navigator.send_stop_signal()
            self.data_collect.stop_collecting()
            print("All tasks stopped.")

# 示例：假设你已经实现了 data_collect、navigator、localizer 类，
# 可以如下方式启动任务管理器
if __name__ == '__main__':
    # 以下三个类需要你自己实现或替换为实际实现：
    from dummy_classes import DummyDataCollect, DummyNavigator, DummyLocalizer  # 示例导入

    data_collect = DummyDataCollect()       # 采集数据的类
    navigator    = DummyNavigator()          # 用于获取GPS/IMU数据的类
    localizer    = DummyLocalizer()          # 负责计算定位信息的类

    manager = DataCollectManager(data_collect, navigator, localizer)
    manager.start()
