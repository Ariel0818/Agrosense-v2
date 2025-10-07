import cv2
import os

# 输入和输出文件夹路径
input_folder = '/Volumes/LaCie/Agrosense2/data_2025_7_22/data/033422071163/20250714_2046/rgb'    # 原始图像所在文件夹
output_folder = '/Volumes/LaCie/Agrosense2/data_2025_7_22/data/033422071163/20250714_2046/video2' # 输出图像文件夹

# 如果输出文件夹不存在就创建
os.makedirs(output_folder, exist_ok=True)

# 遍历输入文件夹中的所有文件
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')):
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)

        # 水平翻转图像
        flipped1 = cv2.flip(img, 1)
        # flipped = cv2.flip(flipped1, 0)

        # 保存翻转后的图像
        save_path = os.path.join(output_folder, filename)
        cv2.imwrite(save_path, flipped1)

        print(f'Processed: {filename}')

print('批量翻转完成！')
