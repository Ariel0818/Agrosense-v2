import os
import cv2
import numpy as np
import pyrealsense2 as rs

def convert_bag_to_images(bag_file, output_folder):
    """
    将 .bag 文件中的数据逐帧提取并保存为 RGB 和深度图像。

    :param bag_file: .bag 文件路径
    :param output_folder: 输出文件夹路径
    """
    # 检查输出文件夹是否存在
    rgb_folder = os.path.join(output_folder, "rgb1")
    depth_folder = os.path.join(output_folder, "depth1")
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(depth_folder, exist_ok=True)

    # 初始化 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()

    # 配置为读取 .bag 文件
    config.enable_device_from_file(bag_file, repeat_playback=False)

    # 启动管道
    pipeline.start(config)

    # 获取 playback 控件以便控制读取
    playback = pipeline.get_active_profile().get_device().as_playback()
    playback.set_real_time(False)  # 禁用实时模式以确保逐帧处理

    try:
        frame_count = 0
        while True:
            try:
                # 获取帧
                frames = pipeline.wait_for_frames(timeout_ms=1000)
                
                # 获取颜色帧和深度帧
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    print(f"Skipping incomplete frame {frame_count}")
                    continue

                # 转换为 numpy 数组
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # 保存图像
                rgb_path = os.path.join(rgb_folder, f"{frame_count:06d}.png")
                depth_path = os.path.join(depth_folder, f"{frame_count:06d}.png")
                cv2.imwrite(rgb_path, color_image)
                cv2.imwrite(depth_path, depth_image)

                print(f"Saved frame {frame_count:06d}: RGB -> {rgb_path}, Depth -> {depth_path}")
                frame_count += 1

            except RuntimeError:
                # RuntimeError 表示文件到达结尾
                print("Reached end of .bag file.")
                break
    finally:
        pipeline.stop()


# 示例使用
if __name__ == "__main__":
    bag_file = "./Data/20241219_125103.bag"  # 替换为您的 .bag 文件路径
    output_folder = "./Data"  # 输出文件夹路径
    convert_bag_to_images(bag_file, output_folder)
