'''
Show depth and rgb image at the same time with TWO realsense camera
'''

import sys
sys.path.append("/usr/local/OFF")
import pyrealsense2 as rs
import threading
import numpy as np
import cv2
# 创建上下文对象
ctx = rs.context()

# 获取连接到系统上的所有设备
devices = ctx.query_devices()

# 打印每个设备的序列号和名称
for dev in devices:
    print("Device:", dev.get_info(rs.camera_info.serial_number), dev.get_info(rs.camera_info.name))



def camera_thread(device_id):
    # 创建一个上下文对象
    pipeline = rs.pipeline()
    
    # 创建配置对象
    config = rs.config()
    
    # 启用摄像头流
    config.enable_device(device_id)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    # 启动管道
    pipeline.start(config)
    depth_sensor = pipeline.get_active_profile().get_device().query_sensors()[0]
    sensor       = pipeline.get_active_profile().get_device().query_sensors()[1]

    # setting exposure parameters
    sensor.set_option(rs.option.enable_auto_exposure,False)
    sensor.set_option(rs.option.exposure,6)
    sensor.set_option(rs.option.gain, 1)
    # setting white balance
    sensor.set_option(rs.option.enable_auto_white_balance,True)


    
    try:
        while True:
            # 等待一帧数据
            frames = pipeline.wait_for_frames()
    
            # 获取彩色帧
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
    
            if not color_frame or not color_frame:
                continue
    
            # 将帧数据转换为图像
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            images = np.hstack((color_image, depth_colormap))
            # 显示图像
            cv2.namedWindow('RealSense'+device_id,cv2.WINDOW_AUTOSIZE)
            cv2.imshow("RealSense" + device_id, images)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    
    finally:
        # 关闭管道以释放资源
        pipeline.stop()

# 定义两个设备ID
device_ids = ['033422071163', '250122075706']
device_ids = ['243222071121', '243222071222']

# 创建两个线程，分别处理两个摄像头
threads = []
for device_id in device_ids:
    thread = threading.Thread(target=camera_thread, args=(device_id,))
    threads.append(thread)
    thread.start()

# 等待所有线程结束
for thread in threads:
    thread.join()
