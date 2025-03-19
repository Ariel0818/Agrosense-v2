import sys
import os
sys.path.append("/usr/local/OFF")
import time
import cv2
import numpy as np
import pyrealsense2 as rs
import multiprocessing
from multiprocessing import Barrier, Process, Value, Queue, Event
from utils.log import LoggerManager
import logging

class DualCamera:
    def __init__(self, device_ids, exposure, gain, width=640, height=480, fps=30):

        # initialize camera parameters
        self.width      = width
        self.height     = height
        self.fps        = fps
        self.device_ids = device_ids
        self.exposure   =  exposure
        self.gain       =  gain
        
        self.pipelines     = []
        self.align_objects = []
        # Check device connection and initialize pipeline
        for device_id in device_ids:
            try:
                pipeline = rs.pipeline()

                config   = rs.config()
                config.enable_device(device_id)
                config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
                config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)

                pipeline.start(config)
                self.pipelines.append(pipeline)
                self.align_objects.append(rs.align(rs.stream.color))
            except Exception as e:
                print(f"Error initializing device {device_id}: {e}")

        # Adjust camera characteristics
        self.sensors = []
        for pipeline in self.pipelines:
            try:
                # Be careful this might be used for depth_sensors
                sensor = pipeline.get_active_profile().get_device().query_sensors()[1]

                # adjust exposure and white balance
                sensor.set_option(rs.option.enable_auto_exposure, True)
                sensor.set_option(rs.option.enable_auto_white_balance, True)
                self.sensors.append(sensor)
            except IndexError as e:
                print(f"Error accessing sensor settings: {e}")
            except Exception as e:
                print(f"Unexpected error in sensor setup: {e}")

        print(device_ids, "Is Connected")

    def capture(self, start_barrier, sync_barrier, frame_count, rgb_queues, depth_queues, stop_event):
        
        start_barrier.wait()  # 等待所有进程准备好再开始采集
        try:
            while not stop_event.is_set():  # 检查停止标志
                try:
                    sync_barrier.wait(timeout=5)  # 确保各个进程同步，设置超时阻止
                except multiprocessing.BrokenBarrierError:
                    print("Barrier timeout, continuing...")
                    time.sleep(0.1)  # 等待一小段时间
                    continue  # 在超时的情况下继续循环

                for i, pipeline in enumerate(self.pipelines):
                    try:
                        frames         = pipeline.wait_for_frames()
                        aligned_frames = self.align_objects[i].process(frames)

                        depth_frame = aligned_frames.get_depth_frame()
                        color_frame = aligned_frames.get_color_frame()

                        if not depth_frame or not color_frame:
                            continue

                        # 检查队列大小，确保不会阻塞
                        if rgb_queues[i].qsize() >= 10:
                            rgb_queues[i].get()  # 移除最旧的数据
                        rgb_queues[i].put_nowait(np.asanyarray(color_frame.get_data()))

                        if depth_queues[i].qsize() >= 10:
                            depth_queues[i].get()  # 移除最旧的数据
                        depth_queues[i].put_nowait(np.asanyarray(depth_frame.get_data()))

                        # 增加帧计数
                        with frame_count.get_lock():
                            frame_count.value += 1
                    except Exception as e:
                        print(f"Error capturing frames from device {self.device_ids[i]}: {e}")

        finally:
            for pipeline in self.pipelines:
                try:
                    pipeline.stop()
                except Exception as e:
                    print(f"Error stopping pipeline for device {self.device_ids[i]}: {e}")
            
            for queue in rgb_queues + depth_queues:
                while not queue.empty():
                    queue.get()
            print("Capture process stopped.")


    def showImage(self, stop_event):
        """
        实时显示两个相机的 RGB 图像，直到 stop_event 被设置。
        :param stop_event: 用于停止显示的事件
        """
        try:
            print("Starting image display for dual cameras...")
            while not stop_event.is_set():
                for i, pipeline in enumerate(self.pipelines):
                    try:
                        # 获取帧数据
                        frames = pipeline.wait_for_frames()
                        aligned_frames = self.align_objects[i].process(frames)

                        color_frame = aligned_frames.get_color_frame()

                        if not color_frame:
                            continue

                        # 转换为 Numpy 格式
                        rgb_image = np.asanyarray(color_frame.get_data())

                        # 显示图像（为每个相机创建独立窗口）
                        window_name = f"Camera {self.device_ids[i]}"
                        cv2.imshow(window_name, rgb_image)

                    except Exception as e:
                        print(f"Error displaying image from camera {self.device_ids[i]}: {e}")

                # 检测键盘输入，如果按下 `q` 键，则退出显示
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_event.set()
                    break

            print("Stopping image display for dual cameras...")
        finally:
            # 确保关闭所有窗口
            cv2.destroyAllWindows()
            print("Image windows closed.")


# # 配置日志
# logging.basicConfig(
#     level=logging.DEBUG,  # 设置日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
#     format='[%(asctime)s] [%(levelname)s] %(message)s',  # 日志格式
#     datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
# )
# logger = logging.getLogger(__name__)  # 获取日志对象

logger_manager = LoggerManager()
logger         = logger_manager.get_logger()

class SingleCamera:
    
    def __init__(self, device_id, exposure, gain, width=640, height=480, fps=30):

        # initialize camera parameters
        self.width     = width
        self.height    = height
        self.fps       = fps
        self.device_id = device_id
        self.exposure  = exposure
        self.gain      = gain

        # debug if the data is really in the queue
        # self.rgb_path = "/home/agrisense/Documents/smartSprayer/data_store/rgb"
        # self.dep_path = "/home/agrisense/Documkents/smartSprayer/data_stor/depth"

        # Check device connection and initialize pipeline
        try:
            logger.info(f"Initializing camera: {self.device_id}")
            self.pipeline = rs.pipeline()

            config        = rs.config()
            config.enable_device(device_id)
            config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)

            self.pipeline.start(config)
            logger.info(f"Camera {self.device_id} started.")
            self.align_object = rs.align(rs.stream.color)

        except IndexError as e:
            logger.error(f"Error accessing sensor settings of device {self.device_id}: {e}")

        except Exception as e:
            logger.error(f"Error initializing device {self.device_id}: {e}")
            raise

        # Adjust camera characteristics
        try:
            # Be careful this might be used for depth_sensors
            self.sensor = self.pipeline.get_active_profile().get_device().query_sensors()[1]

            # adjust exposure and white balance
            self.sensor.set_option(rs.option.enable_auto_exposure, False)
            self.sensor.set_option(rs.option.exposure, self.exposure)
            self.sensor.set_option(rs.option.gain, self.gain)
            self.sensor.set_option(rs.option.enable_auto_white_balance, True)

        except IndexError as e:
            logger.error(f"Error accessing sensor settings of devce {self.device_id}: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in sensor setup of device {self.device_id}: {e}")
            raise

        logger.info(f"{self.device_id} is connected")

    def capture(self, start_barrier, sync_barrier, frame_count, rgb_queue, depth_queue, stop_event):
        
        start_barrier.wait()  # 等待所有进程准备好再开始采集
        try:
            index = 0
            while not stop_event.is_set():  # 检查停止标志
                try:
                    sync_barrier.wait(timeout=5)  # 确保各个进程同步，设置超时阻止
                except Exception as e:
                    logger.warning(f"Barrier timeout for device {self.device_id}: {e}")
                    time.sleep(0.1)  # 等待一小段时间
                    continue  # 在超时的情况下继续循环

                try:
                    frame         = self.pipeline.wait_for_frames()
                    aligned_frame = self.align_object.process(frame)

                    depth_frame = aligned_frame.get_depth_frame()
                    color_frame = aligned_frame.get_color_frame()

                    if not depth_frame or not color_frame:
                        continue

                    # 检查队列大小，确保不会阻塞
                    if rgb_queue.qsize() >= 10:
                        rgb_queue.get()  # 移除最旧的数据
                        rgb_image = np.asanyarray(color_frame.get_data())
                        rgb_queue.put_nowait(rgb_image)
                        # cv2.imwrite(f'{self.rgb_path}/{self.device_id}/{index}.png',rgb_image)
                        logger.info(f"Save rgb data (queue full): {self.device_id}")
                    else:
                        rgb_image = np.asanyarray(color_frame.get_data())
                        rgb_queue.put_nowait(rgb_image)
                        # cv2.imwrite(f'{self.rgb_path}/{self.device_id}/{index}.png',rgb_image)
                        rgb_queue.put_nowait(rgb_image)
                        logger.info(f"Save rgb data (queue not full): {self.device_id}")


                    if depth_queue.qsize() >= 10:
                        depth_queue.get()  # 移除最旧的数据
                        depth_image = np.asanyarray(depth_frame.get_data())
                        rgb_queue.put_nowait(depth_image)
                        # cv2.imwrite(f'{self.rgb_path}/{self.device_id}/{index}.png',depth_image)
                        depth_queue.put_nowait(np.asanyarray(depth_frame.get_data()))
                        logger.info(f"Save Depth data (queue full): {self.device_id}")
                    else:
                        depth_image = np.asanyarray(depth_frame.get_data())
                        rgb_queue.put_nowait(depth_image)
                        # cv2.imwrite(f'{self.rgb_path}/{self.device_id}/{index}.png',depth_image)
                        depth_queue.put_nowait(np.asanyarray(depth_frame.get_data()))
                        logger.info(f"Save Depth data (queue not full): {self.device_id}")


                    # 增加帧计数
                    with frame_count.get_lock():
                        frame_count.value += 1
                        logger.debug(f"Captured frame {frame_count.value} from device {self.device_id}")
                except Exception as e:
                    logger.error(f"Error capturing frames from device {self.device_id}: {e}")

        finally:
            try:
                self.pipeline.stop()
                logger.info(f"Camera {self.device_id} stopped.")
            except Exception as e:
                logger.error(f"Error stopping pipeline for device {self.device_id}: {e}")

            while not rgb_queue.empty()and depth_queue.empty():
                rgb_queue.get()
                depth_queue.get()

    def showImage(self, stop_event):
        """
        显示实时 RGB 图像，直到 stop_event 被设置。
        :param stop_event: 用于停止显示的事件
        """
        try:
            logger.info(f"Starting image display for device {self.device_id}.")

            while not stop_event.is_set():
                # 获取帧数据
                frame = self.pipeline.wait_for_frames()
                aligned_frame = self.align_object.process(frame)

                color_frame = aligned_frame.get_color_frame()

                if not color_frame:
                    continue

                # 转换为 Numpy 格式
                rgb_image = np.asanyarray(color_frame.get_data())

                # 显示图像
                cv2.imshow(f"Camera {self.device_id}", rgb_image)

                # 检测键盘输入，如果按下 `q` 键，则退出显示
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_event.set()
                    break

            logger.info(f"Stopping image display for device {self.device_id}.")
        except Exception as e:
            logger.error(f"Error displaying image for device {self.device_id}: {e}")
        finally:
            # 确保窗口关闭
            cv2.destroyAllWindows()
            logger.info(f"Image window closed for device {self.device_id}.")



########################TEST#######################################################################
def setup_and_run(device_ids, start_barrier, sync_barrier, frame_count, rgb_queues, depth_queues, start_event, stop_event):
    # cam = DualCamera(device_ids)
    logger.info(f"Process for device {device_ids} is starting.")
    cam = SingleCamera(device_ids, exposure, gain, width=640, height=480, fps=30)
    logger.info(f"Device {device_ids} initialized successfully.")
    start_event.wait()
    logger.info(f"Device {device_ids} received start singal.")
    cam.capture(start_barrier, sync_barrier, frame_count, rgb_queues, depth_queues, stop_event)
    logger.info(f"Process for device {device_ids} has ended.")

def rgb_data_consumer(rgb_queue1, rgb_queue2, stop_event):
    logger.info("RGB data consumer started.")

    # test if the image in the queue
    i = 0
    j = 0
    while not stop_event.is_set():
        for queue in rgb_queue1:
            if not queue.empty():
                rgb_image = queue.get()
                # cv2.imwrite(f'/home/agrisense/Documents/smartSprayer/data_store/rgbnew/033422071163/{i}.png', rgb_image)
                # i = i+1
                logger.debug("Processed an RGB frame.")
        for queue in rgb_queue2:
            if not queue.empty():
                rgb_image = queue.get()
                # cv2.imwrite(f'/home/agrisense/Documents/smartSprayer/data_store/rgbnew/033422071163/{j}.png', rgb_image)
                # j = j+1
                logger.debug("Processed an RGB frame.")
    logger.info("RGB data consumer stopped.")

def depth_data_consumer(depth_queue1, depth_queue2, stop_event):
    logger.info("Depth data consumer started.")

    # test if the image in the queue
    i = 0
    j = 0
    while not stop_event.is_set():
        for queue in depth_queue1:
            if not queue.empty():
                depth_image = queue.get()
                # cv2.imwrite(f'/home/agrisense/Documents/smartSprayer/data_store/depthnew/033422071163/{i}.png', rgb_image)
                # i = i+1
                logger.debug("Processed a depth frame.")

        for queue in depth_queue2:
            if not queue.empty():
                depth_image = queue.get()
                # cv2.imwrite(f'/home/agrisense/Documents/smartSprayer/data_store/depthnew/243222071121/{j}.png', rgb_image)
                # j = j+1
    logger.info("Depth data consumer stopped.")



if __name__ == '__main__':

    device_id_pairs    = [('033422071163',), ('243222071121',)]
    width, height, fps =640, 480, 30
    exposure =  8
    gain     = 1

    if len(device_id_pairs[0]) == 2:
        num = 2
    else:
        num = 1

    # 创建两个同步带，分别用于启动和每一帧的同步

    start_barrier = Barrier(parties=len(device_id_pairs))
    sync_barrier  = Barrier(parties=len(device_id_pairs))
    start_event   = Event()
    stop_event    = Event()
    processes     = []

    # 用于计数捕获的帧数
    frame_count_1 = Value('i', 0)  # 用于进程 1 的计数
    frame_count_2 = Value('i', 0)  # 用于进程 2 的计数

    # 创建RGB和深度数据的队列，每个相机都有自己的队列，限制最大长度为10
    rgb_queues_1   = Queue(maxsize=10)
    depth_queues_1 = Queue(maxsize=10)
    rgb_queues_2   = Queue(maxsize=10) 
    depth_queues_2 = Queue(maxsize=10) 

    # 创建并启动两个摄像头进程
    for idx, device_ids in enumerate(device_id_pairs):
        if idx == 0:
            p = Process(target=setup_and_run, args=(device_ids, start_barrier, sync_barrier, frame_count_1, rgb_queues_1, depth_queues_1, start_event, stop_event))
        else:
            p = Process(target=setup_and_run, args=(device_ids, start_barrier, sync_barrier, frame_count_2, rgb_queues_2, depth_queues_2, start_event, stop_event))
        processes.append(p)

    # 创建并启动消费者进程
    rgb_consumer_process   = Process(target=rgb_data_consumer, args=(rgb_queues_1, rgb_queues_2, stop_event,))
    depth_consumer_process = Process(target=depth_data_consumer, args=(depth_queues_1, depth_queues_2, stop_event,))
    processes.extend([rgb_consumer_process, depth_consumer_process])

    # 启动所有进程
    for process in processes:
        process.start()
        logger.info("All processes have been started.")

    start_event.set()
    
    # 等待所有进程完成
    try:
        for process in processes[:len(device_id_pairs)]:
            process.join()

        stop_event.set()

        for process in processes[len(device_id_pairs):]:
            process.join()
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Terminating processes...")
        stop_event.set()
        for process in processes:
            process.terminate()
        for process in processes:
            process.join()

    logger.info(f"Frames captured by Camera 1: {frame_count_1.value}")
    logger.info(f"Frames captured by Camera 2: {frame_count_2.value}")
    