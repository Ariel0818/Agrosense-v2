import sys
import os
import time
import numpy as np
import cv2
import pyrealsense2 as rs
from concurrent.futures import ThreadPoolExecutor
import threading

class DualCamera:
    def __init__(self, device_ids, rgb_paths, depth_paths, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.rgb_paths = rgb_paths
        self.depth_paths = depth_paths
        self.device_ids = device_ids
        
        self.pipelines = []
        self.align_objects = []
        for device_id in device_ids:
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_device(device_id)
            config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
            pipeline.start(config)

            sensor = pipeline.get_active_profile().get_device().query_sensors()[1]
            sensor.set_option(rs.option.enable_auto_exposure, True)
            # if device_id == '250122075706' or device_id == '033422071163':
            #     print("1")
            #     # setting exposure parameters
            #     sensor.set_option(rs.option.exposure,6)
            #     time.sleep(0.1)
            # else:
            #     print("2")
            #     sensor.set_option(rs.option.exposure,6)
            #     time.sleep(0.1)
                
            # sensor.set_option(rs.option.gain, 1)
            # setting white balance
            sensor.set_option(rs.option.enable_auto_white_balance,True)

            self.pipelines.append(pipeline)
            self.align_objects.append(rs.align(rs.stream.color))

        print(device_ids, "已连接")

    def capture(self, start_barrier):
        start_barrier.wait()
        
        try:
            t_start = time.time()
            frame_count = 1
            while time.time() - t_start < 10:  # 运行30秒
            # while True:
                for i, pipeline in enumerate(self.pipelines):
                    frames = pipeline.wait_for_frames()
                    aligned_frames = self.align_objects[i].process(frames)
                    
                    depth_frame = aligned_frames.get_depth_frame()
                    color_frame = aligned_frames.get_color_frame()
                    
                    if not depth_frame or not color_frame:
                        continue
                    
                    depth_image = np.asanyarray(depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())
                    
                    cv2.imwrite(f'{self.rgb_paths[i]}/{frame_count}.png', color_image)
                    cv2.imwrite(f'{self.depth_paths[i]}/{frame_count}_depth.png', depth_image)
                
                frame_count += 1
        finally:
            for pipeline in self.pipelines:
                pipeline.stop()

def setup_and_run(device_ids, rgb_paths, depth_paths, start_barrier):
    cam = DualCamera(device_ids, rgb_paths, depth_paths)
    cam.capture(start_barrier)

if __name__ == '__main__':
    date = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    paths = {
        'left_UP': ('rgb_data', 'dep_data'),
        'left_down': ('rgb_data', 'dep_data'),
        'right_UP': ('rgb_data', 'dep_data'),
        'right_down': ('rgb_data', 'dep_data')
    }

    device_id_pairs = [
        ('250122075706', '033422071163'),
        ('243222071121', '243222071222')
    ]
    
    base_path = './Data'

    start_barrier = threading.Barrier(parties=2)

    executor = ThreadPoolExecutor(max_workers=2)
    futures = []

    path_items = list(paths.items())
    for idx, device_ids in enumerate(device_id_pairs):
        location1, (rgb1, dep1) = path_items[idx * 2]
        location2, (rgb2, dep2) = path_items[idx * 2 + 1]
        
        rgb_path1 = os.path.join(base_path, f'{location1}/{rgb1}_{date}/')
        dep_path1 = os.path.join(base_path, f'{location1}/{dep1}_{date}/')
        rgb_path2 = os.path.join(base_path, f'{location2}/{rgb2}_{date}/')
        dep_path2 = os.path.join(base_path, f'{location2}/{dep2}_{date}/')
        
        os.makedirs(rgb_path1, exist_ok=True)
        os.makedirs(dep_path1, exist_ok=True)
        os.makedirs(rgb_path2, exist_ok=True)
        os.makedirs(dep_path2, exist_ok=True)
        
        futures.append(executor.submit(setup_and_run, device_ids, [rgb_path1, rgb_path2], [dep_path1, dep_path2], start_barrier))

    for future in futures:
        future.result()
