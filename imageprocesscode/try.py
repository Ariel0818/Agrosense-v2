import cv2
import numpy as np
import matplotlib.pyplot as plt

# 读取灰度深度图
depth_original = cv2.imread('014/left/depth_L014/0000122_depth.png', cv2.IMREAD_GRAYSCALE)

# Compute histogram of the original depth image (pixel intensity 0-255)
hist_original = cv2.calcHist([depth_original], [0], None, [256], [0, 256]).flatten()

# Plot the histogram of original depth values
plt.figure(figsize=(10, 4))
plt.plot(hist_original, color='blue')
plt.title("Original Depth Image Histogram")
plt.xlabel("Pixel Intensity (0=Near, 255=Far)")
plt.ylabel("Pixel Count")
plt.grid(True)
plt.tight_layout()

# Save the plot
histogram_original_path = "original_depth_histogram.png"
plt.savefig(histogram_original_path)
plt.close()



import os
from glob import glob

# Define input and output directories
input_dir = "014/left/depth_L014/"
output_dir = "014/left/depth_histograms/"
os.makedirs(output_dir, exist_ok=True)

# Find all PNG depth images in the input directory
depth_images = glob(os.path.join(input_dir, "*.png"))

# Process each image
for depth_path in depth_images:
    filename = os.path.basename(depth_path)
    name, ext = os.path.splitext(filename)

    # Read grayscale depth image
    depth_img = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
    if depth_img is None:
        continue

    # Compute histogram
    hist = cv2.calcHist([depth_img], [0], None, [256], [0, 256]).flatten()

    # Plot histogram
    plt.figure(figsize=(10, 4))
    plt.plot(hist, color='blue')
    plt.title(f"Depth Histogram: {name}")
    plt.xlabel("Pixel Intensity (0=Near, 255=Far)")
    plt.ylabel("Pixel Count")
    plt.grid(True)
    plt.tight_layout()

    # Save histogram plot
    save_path = os.path.join(output_dir, f"{name}_his.png")
    plt.savefig(save_path)
    plt.close()

# List saved histogram files
sorted(glob(os.path.join(output_dir, "*.png")))
