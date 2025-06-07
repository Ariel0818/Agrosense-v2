import cv2

# 读取图像
img = cv2.imread('014/left/filtered_data_L14-55/0000160.png')

# 显示图像并手动选择ROI（按回车键确认，Esc键取消）
roi = cv2.selectROI("Select ROI (press ENTER to confirm)", img, showCrosshair=True)

cv2.destroyAllWindows()

# 输出坐标
x, y, w, h = roi
print(f"Selected ROI: x={x}, y={y}, w={w}, h={h}")
