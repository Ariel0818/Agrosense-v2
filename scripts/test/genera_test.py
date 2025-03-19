import cv2

cv2.namedWindow("Test Window")
print("请在窗口激活后，按下 →（右箭头）或者 ←（左箭头）")

while True:
    key = cv2.waitKey(0)
    print(f"按下的键值: {key}")  # 这里会打印出你按下的键的值

    if key == 27:  # ESC 退出
        break

cv2.destroyAllWindows()
