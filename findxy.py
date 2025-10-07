import cv2

# 回调函数：当鼠标点击图像时触发
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: x={x}, y={y}")
        # 在图像上显示坐标
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f'({x},{y})', (x, y), font, 0.5, (0, 255, 0), 1)
        cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
        cv2.imshow('Image', img)

# 加载图像
img = cv2.imread('your_image.jpg')  # 替换为你的图片路径
cv2.imshow('Image', img)

# 注册鼠标回调函数
cv2.setMouseCallback('Image', click_event)

# 等待按键退出
cv2.waitKey(0)
cv2.destroyAllWindows()
