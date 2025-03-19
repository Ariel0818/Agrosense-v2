import sys, os, random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget,
    QLabel, QSizePolicy, QFrame, QSpacerItem, QLineEdit, QComboBox
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController, QCylinderMesh, QPhongMaterial, QCuboidMesh
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QSceneLoader
from PyQt5.QtGui import QVector3D, QQuaternion

# ----- 工具函数 ----- #
def create_coordinate_axes(parent):
    """在 parent 节点下创建三个坐标轴（X: 红色, Y: 绿色, Z: 蓝色）"""
    axis_length = 5.0
    axis_radius = 0.05

    # X轴（红色，绕 Z 轴旋转90°）
    x_axis = QEntity(parent)
    x_mesh = QCylinderMesh()
    x_mesh.setRadius(axis_radius)
    x_mesh.setLength(axis_length)
    x_transform = QTransform()
    x_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), 90))
    x_material = QPhongMaterial(parent)
    x_material.setDiffuse(QColor(255, 0, 0))
    x_axis.addComponent(x_mesh)
    x_axis.addComponent(x_transform)
    x_axis.addComponent(x_material)

    # Y轴（绿色）
    y_axis = QEntity(parent)
    y_mesh = QCylinderMesh()
    y_mesh.setRadius(axis_radius)
    y_mesh.setLength(axis_length)
    y_transform = QTransform()  # 默认沿 Y 轴，无需旋转
    y_material = QPhongMaterial(parent)
    y_material.setDiffuse(QColor(0, 255, 0))
    y_axis.addComponent(y_mesh)
    y_axis.addComponent(y_transform)
    y_axis.addComponent(y_material)

    # Z轴（蓝色，绕 X 轴旋转90°）
    z_axis = QEntity(parent)
    z_mesh = QCylinderMesh()
    z_mesh.setRadius(axis_radius)
    z_mesh.setLength(axis_length)
    z_transform = QTransform()
    z_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 90))
    z_material = QPhongMaterial(parent)
    z_material.setDiffuse(QColor(0, 0, 255))
    z_axis.addComponent(z_mesh)
    z_axis.addComponent(z_transform)
    z_axis.addComponent(z_material)

def create_car_entity(car_entity):
    """
    在 car_entity 节点下加载车辆模型（这里用 DAE 文件示例，也可以用 QCuboidMesh 替代）
    注意：如果同时添加了长方体模型和 DAE 模型，可能会互相覆盖，请根据实际需要选择加载哪一个
    """
    # 创建 Transform，用于后续控制车辆位置和旋转
    car_transform = QTransform()
    car_transform.setTranslation(QVector3D(0, 0, 0))
    car_transform.setScale(0.5)  # 初始缩放（根据模型大小调整）
    
    # 如果你想用长方体模型替代 DAE，可以取消下面几行注释：
    # car_mesh = QCuboidMesh()
    # car_mesh.setXExtent(2)
    # car_mesh.setYExtent(1)
    # car_mesh.setZExtent(4)
    # car_material = QPhongMaterial(car_entity)
    # car_material.setDiffuse(QColor(200, 200, 0))
    # car_entity.addComponent(car_mesh)
    # car_entity.addComponent(car_transform)
    # car_entity.addComponent(car_material)
    
    # 加载 DAE 模型
    car_loader = QSceneLoader(car_entity)
    car_loader.setSource(QUrl.fromLocalFile("/home/hg/Documents/Agrosense/scripts/visualizations/icons/vehicle_body.dae"))
    car_entity.addComponent(car_loader)
    
    return car_transform

# ----- 主窗口类 ----- #
class AgroSenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pages = {}  # 存放各页面的字典
        self.buttons = {}  # 存放左侧按钮（图标菜单）的字典
        self.valid_username = "precag"
        self.valid_password = "precag"
        self.camera_settings = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AgroSense")
        self.setGeometry(100, 100, 1200, 800)

        # 主界面采用左右分栏：左侧工具栏，右侧内容区域（用 QStackedWidget 管理多个页面）
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 左侧工具栏
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color:#e6ffe6;")
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignTop)
        left_widget.setLayout(left_layout)

        # 添加标题
        title_label = QLabel("AgroSense", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color:#2e8b57;")
        left_layout.addWidget(title_label)

        # 按钮样式
        button_style = """
            QPushButton {
                background-color: none;
                border: none;
                color:#006400;
                font-size: 16px;
                text-align: left;
                padding: 8px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
            QPushButton:pressed {
                color:#228b22;
            }
        """
        # 添加左侧按钮（点击后切换右侧页面）
        self.buttons["admin"]   = self.add_main_button(left_layout, "Admin", "path/to/Admin_icon.png", self.show_admin_page, button_style)
        self.buttons["Setting"] = self.add_main_button(left_layout, "Setting", "path/to/Setting.png", self.show_setting_page, button_style)
        self.buttons["START"]   = self.add_main_button(left_layout, "START", "path/to/START.png", self.start_function, button_style)
        self.buttons["Data"]    = self.add_main_button(left_layout, "Data", "path/to/Data.png", self.data_function, button_style)
        self.buttons["DataMap"] = self.add_main_button(left_layout, "DataMap", "path/to/DataMap.png", self.map_function, button_style)
        self.buttons["Logout"]  = self.add_main_button(left_layout, "Logout", "path/to/Logout.png", self.logout_function, button_style)
        # 默认禁用按钮（直到登录成功后开启）
        self.disable_buttons()

        # 中间添加一条分隔线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("color:#006400; width: 1px;")

        # 右侧内容区域：用 QStackedWidget 管理各个页面
        self.right_stack = QStackedWidget()
        
        # 创建各个页面并添加到 QStackedWidget
        self.add_page("admin", self.create_admin_page())
        self.add_page("default", self.create_default_page())
        self.add_page("setting", self.create_setting_page())
        self.add_page("camera_setting", self.create_camera_setting_page())
        self.add_page("gps_setting", self.create_gps_setting_page())
        self.add_page("imu_setting", self.create_IMU_setting_page())
        self.add_page("map", self.create_map_page())

        # 默认显示 "default" 页面
        self.right_stack.setCurrentWidget(self.pages["default"])

        # 将左右两侧添加到主布局中
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(line)
        main_layout.addWidget(self.right_stack, stretch=6)

    def add_main_button(self, layout, text, icon_path, callback, style):
        """创建左侧工具栏按钮并添加到 layout 中"""
        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def add_page(self, name, page):
        """将页面添加到 QStackedWidget 中，并保存到 pages 字典"""
        self.pages[name] = page
        self.right_stack.addWidget(page)

    # ----- 各页面的创建函数（可根据需要进一步封装为独立类） ----- #
    def create_admin_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        # 示例：简单的登录界面
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.admin_login)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addStretch()
        return page

    def create_default_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Welcome to AgroSense Main Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def create_setting_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        # 简单示例：提供进入各设置页面的按钮
        cam_btn = QPushButton("Camera Setting")
        cam_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["camera_setting"]))
        gps_btn = QPushButton("GPS Setting")
        gps_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["gps_setting"]))
        imu_btn = QPushButton("IMU Setting")
        imu_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["imu_setting"]))
        layout.addWidget(cam_btn)
        layout.addWidget(gps_btn)
        layout.addWidget(imu_btn)
        layout.addStretch()
        return page

    def create_camera_setting_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Camera Setting Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        # 此处可添加摄像头参数设置控件
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["setting"]))
        layout.addWidget(back_btn)
        return page

    def create_gps_setting_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("GPS Setting Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        # 此处可添加地图显示等控件
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["setting"]))
        layout.addWidget(back_btn)
        return page

    def create_IMU_setting_page(self):
        """创建包含 3D 视图（坐标轴与车辆实体）以及 IMU 信息的页面"""
        page = QWidget()
        layout = QHBoxLayout(page)
        # 左侧：3D 视图
        self.view = Qt3DWindow()
        container = QWidget.createWindowContainer(self.view)
        container.setMinimumSize(400, 400)
        layout.addWidget(container, 2)
        
        # 创建 3D 场景
        self.scene_root = QEntity()
        create_coordinate_axes(self.scene_root)
        self.car_entity = QEntity(self.scene_root)
        self.car_transform = create_car_entity(self.car_entity)
        
        # 设置摄像机
        camera = self.view.camera()
        camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000.0)
        camera.setPosition(QVector3D(0, 5, 20))
        camera.setViewCenter(QVector3D(0, 0, 0))
        cam_controller = QOrbitCameraController(self.scene_root)
        cam_controller.setCamera(camera)
        self.view.setRootEntity(self.scene_root)
        
        # 右侧：IMU 信息面板
        info_layout = QVBoxLayout()
        self.yaw_label = QLabel("Yaw: 0°")
        self.pitch_label = QLabel("Pitch: 0°")
        self.roll_label = QLabel("Roll: 0°")
        refresh_btn = QPushButton("Refresh IMU")
        refresh_btn.clicked.connect(self.update_IMU_data)
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["setting"]))
        info_layout.addWidget(self.yaw_label)
        info_layout.addWidget(self.pitch_label)
        info_layout.addWidget(self.roll_label)
        info_layout.addWidget(refresh_btn)
        info_layout.addWidget(back_btn)
        layout.addLayout(info_layout, 1)
        return page

    def create_map_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Map Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        # 此处添加 QWebEngineView 或其他地图控件
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.right_stack.setCurrentWidget(self.pages["default"]))
        layout.addWidget(back_btn)
        return page

    # ----- 以下为各页面切换与业务逻辑函数 ----- #
    def admin_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == self.valid_username and password == self.valid_password:
            print("Login successful!")
            self.enable_buttons()
            self.right_stack.setCurrentWidget(self.pages["default"])
        else:
            print("Invalid login. Try again.")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setPlaceholderText("Invalid Username!")
            self.password_input.setPlaceholderText("Invalid Password!")

    def show_admin_page(self):
        self.right_stack.setCurrentWidget(self.pages["admin"])

    def show_setting_page(self):
        self.right_stack.setCurrentWidget(self.pages["setting"])

    def start_function(self):
        print("START button clicked!")
        self.right_stack.setCurrentWidget(self.pages["default"])

    def data_function(self):
        print("Data button clicked!")
        self.right_stack.setCurrentWidget(self.pages["default"])

    def map_function(self):
        print("DataMap button clicked!")
        self.right_stack.setCurrentWidget(self.pages["map"])

    def logout_function(self):
        print("Logout button clicked!")
        # 例如退出登录后禁用部分按钮，切换回登录页面
        self.disable_buttons()
        self.right_stack.setCurrentWidget(self.pages["admin"])

    def update_IMU_data(self):
        """模拟更新 IMU 数据并更新车辆朝向"""
        angles = [
            round(random.uniform(-180, 180), 2),  # Yaw
            round(random.uniform(-90, 90), 2),    # Pitch
            round(random.uniform(-180, 180), 2)     # Roll
        ]
        self.yaw_label.setText(f"Yaw: {angles[0]}°")
        self.pitch_label.setText(f"Pitch: {angles[1]}°")
        self.roll_label.setText(f"Roll: {angles[2]}°")
        yaw = QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), angles[0])
        pitch = QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), angles[1])
        roll = QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), angles[2])
        combined = yaw * pitch * roll
        self.car_transform.setRotation(combined)

    def disable_buttons(self):
        """禁用左侧按钮（除 Admin 外）"""
        for key, btn in self.buttons.items():
            if key != "admin":
                btn.setEnabled(False)

    def enable_buttons(self):
        """启用所有左侧按钮"""
        for btn in self.buttons.values():
            btn.setEnabled(True)

    # 你还可以在此处添加更多业务逻辑函数

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgroSenseApp()
    window.show()
    sys.exit(app.exec_())
