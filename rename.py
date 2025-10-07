import os
import shutil

def copy_and_rename_files(source_folder, target_folder, prefix="13R_"):
    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # 确保是文件（不是目录）
        if os.path.isfile(source_path):
            new_filename = prefix + filename  
            target_path = os.path.join(target_folder, new_filename)

            # 复制文件
            shutil.copy2(source_path, target_path)
            print(f"Copied: {filename} -> {new_filename}")

# 设置源文件夹和目标文件夹
source_folder = "train_R13_dataset1"  # 这里替换成你的原始文件夹路径
target_folder = "renametrain_R13"  # 这里替换成你的目标文件夹路径

# 运行函数
copy_and_rename_files(source_folder, target_folder)
