import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import folium
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QFrame, QSizePolicy, QStackedWidget, QGroupBox, QLineEdit, QSpacerItem, QComboBox, QGridLayout
)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QSize, Qt, QUrl, QTimer, pyqtSignal

from utils.log import LoggerManager

logger_manager = LoggerManager()
logger = logger_manager.get_logger()


class CameraPage(QWidget):
    # 用于切换回上一级页面的信号
    backClicked = pyqtSignal()
    # 定义信号，用于跨线程更新UI，参数为设备ID和 QImage 对象
    updateFrame = pyqtSignal(str, QImage)

    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.taskManager = task_manager
        # 存储各相机的最新图像
        self.latest_frames = {}
        self.create_camera_setting_page()
        # 信号连接：采集线程回传的图像通过信号更新界面
        self.updateFrame.connect(self.on_update_frame)
        # 调用 TaskManager 启动所有相机采集，并传入回调函数
        self.taskManager.show_all_cameras(self.handle_new_frame)

    def create_camera_setting_page(self):
        """
        界面布局：
          - 上部预览框（显示当前选中相机图像，自适应空间，不预设固定尺寸）
          - 下部一行控件：下拉框选择相机、曝光和增益输入框、Apply 按钮
          - 底部 Back 按钮
        """
        main_layout = QVBoxLayout(self)
        # 调整整体布局的间距和边距，减少标题与预览框之间的距离
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 标题区域（与预览框间距较小）
        title_label = QLabel("Camera Setting", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 5px;")
        main_layout.addWidget(title_label)
        
        # 预览区域：不预设固定尺寸，使用 Expanding 策略自适应窗口大小
        self.camera_display = QLabel("Camera View", self)
        self.camera_display.setAlignment(Qt.AlignCenter)
        self.camera_display.setStyleSheet("background-color: black;")
        self.camera_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.camera_display)
        
        # 下部参数设置区域
        bottom_layout = QHBoxLayout()
        
        # 获取相机参数（数量和设备ID列表）
        self.cam_count, self.cam_list = self.taskManager.extract_camera_parameters()
        logger.info(f"Detected {self.cam_count} cameras: {self.cam_list}")
        
        # 下拉框选择相机
        self.camera_select = QComboBox(self)
        self.camera_select.addItems(self.cam_list)
        self.camera_select.currentIndexChanged.connect(self.on_camera_selection_changed)
        bottom_layout.addWidget(self.camera_select)
        
        # 曝光输入
        exposure_label = QLabel("Exposure:", self)
        bottom_layout.addWidget(exposure_label)
        self.exposure_input = QLineEdit(self)
        self.exposure_input.setPlaceholderText("Enter Exposure")
        bottom_layout.addWidget(self.exposure_input)
        
        # 增益输入
        gain_label = QLabel("Gain:", self)
        bottom_layout.addWidget(gain_label)
        self.gain_input = QLineEdit(self)
        self.gain_input.setPlaceholderText("Enter Gain")
        bottom_layout.addWidget(self.gain_input)
        
        # Apply 按钮
        apply_button = QPushButton("Apply Camera Parameter", self)
        apply_button.clicked.connect(self.applyCameraSettings)
        bottom_layout.addWidget(apply_button)
        
        main_layout.addLayout(bottom_layout)
        
        # 底部 Back 按钮区域
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 5px;")
        back_button.clicked.connect(self.backClicked.emit)
        back_layout.addWidget(back_button)
        main_layout.addLayout(back_layout)

    def on_camera_selection_changed(self):
        """当下拉框选择变化时，更新预览显示当前相机的最新图像（若已有）"""
        selected_cam = self.camera_select.currentText()
        if selected_cam in self.latest_frames:
            self.camera_display.setPixmap(QPixmap.fromImage(self.latest_frames[selected_cam]))
        else:
            self.camera_display.setText("No frame received yet.")

    def applyCameraSettings(self):
        """应用当前下拉框选中相机的设置，示例中只打印日志"""
        selected_cam = self.camera_select.currentText()
        exposure = self.exposure_input.text()
        gain = self.gain_input.text()
        logger.info(f"Applying settings for {selected_cam}: Exposure={exposure}, Gain={gain}")
        # 此处可扩展，将参数传递给 TaskManager 或相机接口

    def handle_new_frame(self, device_id, qimg):
        """
        采集线程中调用的回调函数，不能直接更新UI，
        通过发射信号传递到主线程进行更新
        """
        self.updateFrame.emit(device_id, qimg)

    def on_update_frame(self, device_id, qimg):
        """
        信号槽：收到新的图像数据后，存储该图像并在当前选中相机时更新预览显示
        """
        self.latest_frames[device_id] = qimg
        if self.camera_select.currentText() == device_id:
            self.camera_display.setPixmap(QPixmap.fromImage(qimg))


if __name__ == '__main__':
    # 示例运行代码：请确保自行实现或替换 TaskManager 接口
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # 这里提供一个 DummyTaskManager 用于演示
    class DummyTaskManager:
        def extract_camera_parameters(self):
            return (2, ["cam1", "cam2"])
        def show_all_cameras(self, callback):
            # 模拟调用采集线程，将随机图像回传（仅用于演示）
            from PyQt5.QtGui import QImage, QPainter, QColor
            import threading, time
            def simulate():
                while True:
                    for cam in ["cam1", "cam2"]:
                        img = QImage(640, 480, QImage.Format_RGB32)
                        img.fill(QColor("blue"))
                        callback(cam, img)
                    time.sleep(0.5)
            t = threading.Thread(target=simulate, daemon=True)
            t.start()
    
    dummy_task_manager = DummyTaskManager()
    window = CameraPage(dummy_task_manager)
    window.show()
    sys.exit(app.exec_())
