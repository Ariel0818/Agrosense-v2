import time
import sys
import os
sys.path.append("/usr/local/OFF")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import multiprocessing
from multiprocessing import Barrier, Process, Value, Queue, Manager
from queue import Empty
import threading

from imageshow.show_rgb import start_rgb_stream
from manager.data_collect_manager import DataCollectManager
from manager.camera_manager import CameraManager
from localization.agro_nav import USB2Navigator
from manager.realtime_manager import RealTimeProcessManager
from manager.post_process_manager import PostProcessManager
# device_id_pairs = [('033422071163', '250122075706'), ('243222071121', '243222071222')]
device_id_pairs    = [('033422971163',), ('250122075706',)]
width, height, fps = 480, 640, 30
exposure =  8
gain     = 1

class TaskManager:
    
    def __init__(self, device_id_pairs, camera_parameters, width, height, fps):
        self.device_id_pairs = device_id_pairs
        self.width  = width
        self.height = height
        self.fps    = fps
        self.camera_params = camera_parameters
        self.USB2Nav = USB2Navigator()
        #self.cameraManager = CameraManager()
        
    def initialization():
        pass

    def extract_camera_parameters(self):
        """
        计算参数总数，并返回所有参数的列表
        :param device_id_pairs: List[Tuple[str, str]] -> 设备 ID 组成的列表
        :return: (int, List[str]) -> (参数总数, 所有参数列表)
        """
        all_params = [device_id for pair in self.device_id_pairs for device_id in pair]  # 展开所有元组元素
        return len(all_params), all_params  # 返回参数总数和展开后的列表

    def show_all_cameras(self, image_callback):
        """
        对所有相机启动图像采集（只采集RGB图像），并通过 image_callback(device_id, QImage)
        将采集到的图像传递出去。
        :param image_callback: 回调函数，用于传出采集的图像数据
        """
        count, camera_list = self.extract_camera_parameters()
        print(f"检测到 {count} 个相机: {camera_list}")
        threads = []
        for device_id in camera_list:
            # 根据设备ID从 camera_params 中获取对应的曝光和增益
            params = self.camera_params.get(device_id, {})
            exposure = params.get('exposure', 8)  # 如果没有指定，则使用默认值8
            gain = params.get('gain', 1)          # 默认值1

            t = threading.Thread(
                target=start_rgb_stream,
                args=(device_id, self.width, self.height, self.fps, exposure, gain, image_callback)
            )
            t.daemon = True  # 主程序退出时，线程自动结束
            t.start()
            threads.append(t)
        # 如有需要，可等待所有线程结束（通常GUI程序中不建议阻塞）
        # for t in threads:
        #     t.join()

    def dataCollectTask(self):
        # self.dataCollector = DataCollectManager(self.cameraManager)
        # self.dataCollector.start()
        pass


    def realtime_proces_task(self):
        # self.realtimeProcessor = RealTimeProcessManager(self.cameraManager)
        # self.realtimeProcessor.start()
        pass
        

    def data_process_task(self):
        self.postProcessor = PostProcessManager()
        self.postProcessor.start()
        pass

    
    def saveToJson():
        '''
        Save data to .Json file for temperory storage
        '''
        pass

    def saveToDatabase():
        '''
        Transfer all the result to the Database
        '''
        pass

    def savePosition():
        '''
        Record the position of the camera
        '''
        pass

    def mapeResult():
        '''
        Map all the result to the MAP
        '''
        pass

