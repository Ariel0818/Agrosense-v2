import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import folium
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QFrame, QSizePolicy, QStackedWidget, QGroupBox, QLineEdit, QSpacerItem, QComboBox
)
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPolygonF, QColor, QPen, QBrush
from PyQt5.QtCore import QSize, Qt, QUrl, QTimer, pyqtSignal, QPointF
# 以下3D相关的导入保留，若系统其他部分需要使用可继续使用
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController, QCylinderMesh, QPhongMaterial, QCuboidMesh
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QMaterial, QSceneLoader
from PyQt5.QtGui import QVector3D, QQuaternion

from utils.log import LoggerManager

logger_manager = LoggerManager()
logger = logger_manager.get_logger()

# 采用 QPainter 绘制类似 Google 地图中方向指示的箭头
class ArrowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0  # 初始角度（单位：度）
        self.setMinimumSize(400, 400)
    
    def setAngle(self, angle):
        self.angle = angle
        self.update()  # 重绘

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 将坐标系原点移动到窗口中心
        center = self.rect().center()
        painter.translate(center)
        # 根据 yaw 值旋转（正角度为逆时针旋转）
        painter.rotate(self.angle)
        
        # 定义箭头形状（默认指向上方）
        arrow = QPolygonF([
            QPointF(0, -60),   # 箭头尖端
            QPointF(20, 20),   # 右侧外角
            QPointF(10, 20),   # 右侧内凹
            QPointF(10, 60),   # 右下角
            QPointF(-10, 60),  # 左下角
            QPointF(-10, 20),  # 左侧内凹
            QPointF(-20, 20)   # 左侧外角
        ])
        
        pen = QPen(QColor(0, 120, 255), 2)
        brush = QBrush(QColor(0, 120, 255, 180))  # 半透明蓝色
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPolygon(arrow)

# 修改后的 IMU 页面：将显示部分替换为 ArrowWidget 箭头
class ImuPage(QWidget):
    backClicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_IMU_setting_page()

    def create_IMU_setting_page(self):
        """ 创建 IMU 设置页面，显示 2D 箭头及信息面板 """
        page = QWidget()
        layout = QHBoxLayout(self)
        
        # 用箭头替换原来的 3D 视图
        self.arrow_widget = ArrowWidget(self)
        layout.addWidget(self.arrow_widget, 2)  # 箭头显示占 2/3 界面
        
        # 右侧信息面板
        info_layout = QVBoxLayout()
        
        self.yaw_label = QLabel("Yaw: 0°")
        self.pitch_label = QLabel("Pitch: 0°")
        self.roll_label = QLabel("Roll: 0°")
        info_layout.addWidget(self.yaw_label)
        info_layout.addWidget(self.pitch_label)
        info_layout.addWidget(self.roll_label)
        
        self.refresh_IMU_button = QPushButton("Refresh IMU")
        self.refresh_IMU_button.clicked.connect(self.update_IMU_data)
        info_layout.addWidget(self.refresh_IMU_button)
        
        backButton = QPushButton("Back")
        backButton.clicked.connect(self.backClicked.emit)
        info_layout.addWidget(backButton)
        
        layout.addLayout(info_layout, 1)  # 信息面板占 1/3 界面

    def update_IMU_data(self):
        """ 模拟更新 IMU 数据，并根据 yaw 数据更新箭头方向 """
        self.angles = [
            round(random.uniform(-180, 180), 2),  # Yaw
            round(random.uniform(-90, 90), 2),    # Pitch
            round(random.uniform(-180, 180), 2)     # Roll
        ]
        
        self.yaw_label.setText(f"Yaw: {self.angles[0]}°")
        self.pitch_label.setText(f"Pitch: {self.angles[1]}°")
        self.roll_label.setText(f"Roll: {self.angles[2]}°")
        
        # 只根据 yaw 更新 2D 箭头方向
        self.arrow_widget.setAngle(self.angles[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImuPage()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
