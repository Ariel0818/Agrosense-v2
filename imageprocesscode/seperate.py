import cv2
import numpy as np

img = cv2.imread('014/left/filtered_data_L14-55/0000142.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 例如：分割绿色（树木）
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])
mask_green = cv2.inRange(hsv, lower_green, upper_green)

# 分割蓝色（天空）
lower_blue = np.array([90, 50, 50])
upper_blue = np.array([130, 255, 255])
mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

# 分割后进行形态学处理，去噪、连通等
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel, iterations=2)
mask_blue  = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel, iterations=2)

cv2.imshow("Trees Mask", mask_green)
cv2.imshow("Sky Mask", mask_blue)
cv2.waitKey(0)
cv2.destroyAllWindows()
