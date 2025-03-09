import sys
import os
sys.path.append("/usr/local/OFF")
import pyrealsense2 as rs
import time
import os
import json
import multiprocessing
from multiprocessing import Process, Barrier, Value

class SingleCamera:
    def __init__(self, device_id, width=640, height=480, fps=30, exposure=100, gain=16):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.exposure = exposure
        self.gain = gain
        self.pipeline = rs.pipeline()
        self.align_object = rs.align(rs.stream.color)
        
        config = rs.config()
        config.enable_device(device_id)
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.pipeline.start(config)

        self.sensor = self.pipeline.get_active_profile().get_device().query_sensors()[1]
        self.sensor.set_option(rs.option.enable_auto_white_balance, True)
        self.sensor.set_option(rs.option.enable_auto_exposure, False)
        self.sensor.set_option(rs.option.exposure, self.exposure)
        self.sensor.set_option(rs.option.gain, self.gain)

        # 创建存储路径
        self.save_dir = f"data/{device_id}"
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(f"{self.save_dir}/rgb", exist_ok=True)
        os.makedirs(f"{self.save_dir}/depth", exist_ok=True)

        # JSON 存储
        self.json_data = []
        self.json_index = 0
        self.image_counter = 0  # 计数总图像数

        print(device_id, "已连接")

    def save_json(self):
        """ 每 10,000 张图片存储一个 JSON 文件 """
        json_filename = f"{self.save_dir}/metadata_{self.json_index}.json"
        with open(json_filename, "w") as json_file:
            json.dump(self.json_data, json_file, indent=4)
        print(f"Saved JSON: {json_filename}")
        self.json_data = []  # 清空数据
        self.json_index += 1  # 更新 JSON 文件编号

    def capture(self, start_barrier, sync_barrier, frame_count):
        start_barrier.wait()  # 等待所有进程准备好再开始采集
        try:
            t_start = time.time()
            while time.time() - t_start < 300:  # 运行 300 秒（5 分钟）
                try:
                    sync_barrier.wait(timeout=5)  # 确保各个进程同步，设置超时防止阻塞
                except multiprocessing.BrokenBarrierError:
                    print("Barrier timeout, continuing...")
                    break

                frames = self.pipeline.wait_for_frames()
                aligned_frames = self.align_object.process(frames)

                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                if not depth_frame or not color_frame:
                    continue

                timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())  # 生成时间戳
                rgb_filename = f"{self.save_dir}/rgb/image_{timestamp}_{self.image_counter:06}.png"
                depth_filename = f"{self.save_dir}/depth/depth_{timestamp}_{self.image_counter:06}.png"

                # 仅计数，避免保存图像的耗时操作
                with frame_count.get_lock():
                    frame_count.value += 1

                # 存储图像元数据
                self.json_data.append({
                    "timestamp": timestamp,
                    "rgb_path": rgb_filename,
                    "depth_path": depth_filename,
                    "device_id": self.device_id
                })

                # 每 10,000 张图片保存一个 JSON 文件
                if len(self.json_data) >= 1000:
                    self.save_json()

                self.image_counter += 1  # 计数

        finally:
            # 停止相机
            self.pipeline.stop()

            # 保存剩余数据（不足 10,000 张）
            if self.json_data:
                self.save_json()


def setup_and_run(device_id, start_barrier, sync_barrier, frame_count):
    cam = SingleCamera(device_id)
    cam.capture(start_barrier, sync_barrier, frame_count)


if __name__ == '__main__':
    device_id_pairs = [
        '033422071163',
        '243222071121'
    ]

    # 创建两个同步屏障，分别用于启动和每一帧的同步
    start_barrier = Barrier(parties=len(device_id_pairs))
    sync_barrier = Barrier(parties=len(device_id_pairs))

    processes = []

    # 用于计数捕获的帧数
    frame_counts = [Value('i', 0) for _ in device_id_pairs]

    # 创建并启动每个设备对应的进程
    for idx, device_id in enumerate(device_id_pairs):
        frame_count = frame_counts[idx]
        p = Process(target=setup_and_run, args=(device_id, start_barrier, sync_barrier, frame_count))
        processes.append(p)

    # 启动所有进程
    for process in processes:
        process.start()

    # 等待所有进程完成
    for process in processes:
        process.join()

    # 输出每个进程的帧计数
    for idx, frame_count in enumerate(frame_counts):
        print(f"设备 {device_id_pairs[idx]} 捕获的帧数: {frame_count.value}")
