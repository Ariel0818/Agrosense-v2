import os
import time
import numpy as np
import cv2
import pyrealsense2 as rs

def create_directories(base_path, date):
    """Create directories for RGB and depth images."""
    rgb_path = os.path.join(base_path, f'rgb_{date}')
    depth_path = os.path.join(base_path, f'depth_{date}')
    os.makedirs(rgb_path, exist_ok=True)
    os.makedirs(depth_path, exist_ok=True)
    return rgb_path, depth_path

def initialize_pipelines(device_ids, width=640, height=480, fps=30):
    """Initialize pipelines for the given device IDs."""
    pipelines = []
    align_objects = []
    for device_id in device_ids:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(device_id)
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)

        pipeline.start(config)
        pipelines.append(pipeline)
        align_objects.append(rs.align(rs.stream.color))
    return pipelines, align_objects

def capture_images(pipelines, align_objects, rgb_path, depth_path, duration=10):
    """Capture RGB and aligned depth images from the pipelines."""
    start_time = time.time()
    frame_count = 1
    try:
        while time.time() - start_time < duration:
            for i, pipeline in enumerate(pipelines):
                frames = pipeline.wait_for_frames()
                aligned_frames = align_objects[i].process(frames)

                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                # Convert frames to numpy arrays
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # Save images
                cv2.imwrite(f'{rgb_path}/camera_{i + 1}_frame_{frame_count}.png', color_image)
                cv2.imwrite(f'{depth_path}/camera_{i + 1}_frame_{frame_count}_depth.png', depth_image)

            frame_count += 1
    finally:
        for pipeline in pipelines:
            pipeline.stop()

if __name__ == '__main__':
    # Device IDs of the cameras
    device_ids = ['250122075706', '033422071163', '243222071121', '243222071222']

    # Base directory for saving images
    base_path = './Data'
    date = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    # Create directories for saving images
    rgb_path, depth_path = create_directories(base_path, date)

    # Initialize pipelines
    pipelines, align_objects = initialize_pipelines(device_ids)

    # Capture images
    capture_images(pipelines, align_objects, rgb_path, depth_path, duration=10)
