import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import folium
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QFrame, QSizePolicy, QStackedWidget, QGroupBox, QLineEdit,QSpacerItem, QComboBox, QGridLayout
)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QSize, Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView  # 用于显示地图

from utils.log import LoggerManager
from visualizations.camera_page import CameraPage
from visualizations.gps_page import GpsPage
from visualizations.imu_page import ImuPage
from visualizations.map_page import DataMapPage
from visualizations.data_page import DataPage
from visualizations.start_page import StartPage
from visualizations.process_page import DataProcess

logger_manager = LoggerManager()
logger = logger_manager.get_logger()

class AgroSenseApp(QMainWindow):
    def __init__(self, task_manager, parent=None):
        super().__init__()

        self.taskManager = task_manager

        # Initialize the page dictionary
        self.pages = {}
        self.valid_username = "precag"
        self.valid_password = "precag"

        # store camera settings
        self.camera_settings = {}
        self.buttons         = {}

        self.initUI()

    def initUI(self):
        # Initialize main page
        logger.info(f"Initializing UI")
        self.create_main_page()

        # Add Admin page, and set to default
        admin_page = self.create_admin_page()
        self.pages["admin"] = admin_page
        self.right_stack.addWidget(admin_page)
        self.right_stack.setCurrentWidget(self.pages["admin"])

        # Add Default page
        default_page = self.create_default_page()
        self.pages["default"] = default_page
        self.right_stack.addWidget(default_page)

        # Add more pages
        self.cameraPage = CameraPage(self.taskManager)
        self.gpsPage    = GpsPage()
        self.imuPage    = ImuPage()
        
        # Add setting page
        setting_page = self.create_setting_page() 
        self.pages["setting"] = setting_page
        self.right_stack.addWidget(setting_page)

        self.cameraPage.backClicked.connect(self.goto_setting)
        self.add_page("camera_setting",self.cameraPage)
        self.gpsPage.backClicked.connect(self.goto_setting)
        self.add_page("gps_setting",self.gpsPage)
        self.imuPage.backClicked.connect(self.goto_setting)
        self.add_page("imu_setting", self.imuPage)

        self.dataMapPage = DataMapPage()
        self.add_page("map", self.dataMapPage)
        self.dataPage = DataPage()
        self.add_page("data",self.dataPage)
        self.startPage = StartPage(self.taskManager)
        self.add_page("start", self.startPage)
        self.processPage = DataProcess()
        self.add_page("process", self.processPage)

        

    def create_main_page(self):
        logger.info(f"Create main page")
        # Design main page
        self.setWindowTitle("AgroSense")
        self.setGeometry(100, 100, 1200, 800)

        # Main page layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Left toolbar
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color:#e6ffe6;")
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignTop)
        left_widget.setLayout(left_layout)

        # Add title
        title_label = QLabel("AgroSense", self)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color:#2e8b57;
            }
        """)
        left_layout.addWidget(title_label)

        # Define the type of button
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

        # Add buttons
        self.buttons["admin"]   = self.add_main_button(left_layout, "Admin", os.path.join( "scripts/visualizations/icons", "Admin_icon.png"), self.admin_function, button_style)
        self.buttons["Setting"] = self.add_main_button(left_layout, "Setting", os.path.join( "scripts/visualizations/icons", "Setting.png"), self.setting_function, button_style)
        self.buttons["START"]   = self.add_main_button(left_layout, "START", os.path.join( "scripts/visualizations/icons", "START.png"), self.start_function, button_style)
        self.buttons["Data"]    = self.add_main_button(left_layout, "Data", os.path.join( "scripts/visualizations/icons", "Data.png"), self.data_function, button_style)
        self.buttons["Process"] = self.add_main_button(left_layout, "Process", os.path.join( "scripts/visualizations/icons", "dataProcess.png"),self.data_process, button_style)
        self.buttons["DataMap"] = self.add_main_button(left_layout, "DataMap", os.path.join( "scripts/visualizations/icons", "DataMap.png"), self.map_function, button_style)
        self.buttons["Logout"]  = self.add_main_button(left_layout, "Logout", os.path.join( "scripts/visualizations/icons", "Logout.png"), self.logout_function, button_style)
        
        # disable the function of button
        self.disable_buttons()

        # Create a vertical line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("color:#006400; width: 1px;")

        # Create right content：`QStackedWidget`
        self.right_stack = self.create_right_stack()

        # Setting the scale
        main_layout.addWidget(left_widget, stretch=1.5)
        main_layout.addWidget(line)
        main_layout.addWidget(self.right_stack, stretch=6)

    def add_page(self, name, page):
        """将页面添加到 QStackedWidget 中，并保存到 pages 字典"""
        self.pages[name] = page
        self.right_stack.addWidget(page)

    # Add a button with an icon
    def add_main_button(self, layout, text, icon_path, callback, style):

        
        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    # Create the content area on the right
    def create_right_stack(self):
        """
        Create the content area on the right (use QStackedWidget to manage multiple pages).
        By default, a page showing "Content Area" is added. 
        """
        right_stack = QStackedWidget()
        
        # Default page: contains a QLabel showing "Content Area"
        default_page = QWidget()
        layout = QVBoxLayout()
        self.content_label = QLabel("Content Area", self)
        self.content_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.content_label)
        default_page.setLayout(layout)

        right_stack.addWidget(default_page)

        return right_stack

    def create_admin_page(self):
        """Create Admin page with centered layout."""
        page = QWidget()
        layout = QVBoxLayout()
        
        # make title up
        layout.addItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFixedWidth(200)
        
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)  # 隐藏密码输入
        self.password_input.setFixedWidth(200)
        
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(100)
        self.login_button.clicked.connect(self.admin_login)
        
        # vertical distribution
        form_layout = QVBoxLayout()
        # form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)  # Centerize
        
        username_layout = QHBoxLayout()
        username_layout.addStretch()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        username_layout.addStretch()
        
        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.addStretch()
        
        input_layout.addLayout(username_layout)
        input_layout.addSpacing(10)  # add space
        input_layout.addLayout(password_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addSpacing(400)  # add space
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        input_layout.addSpacing(10)  # 
        input_layout.addLayout(button_layout)
        
        form_layout.addLayout(input_layout)  # 这里去掉 alignment 参数
        
        layout.addLayout(form_layout)
        
        # Add space
        layout.addItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        page.setLayout(layout)
        return page

    def create_default_page(self):
        """Create Defaul page"""
        logger.info(f"Create the default page")
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Welcome to AgroSense Main Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        page.setLayout(layout)
        return page

    def admin_login(self):
        """Verify login"""
        logger.info(f"Wait for log in")
        username = self.username_input.text()
        password = self.password_input.text()

        if username == self.valid_username and password == self.valid_password:
            print("Login successful! Switching to main page...")
            self.enable_buttons()  # enable all the buttons on the left
            # Change to default page
            self.right_stack.setCurrentWidget(self.pages["default"])  
        else:
            print("Invalid login. Try again.")
            self.username_input.setText("")
            self.password_input.setText("")
            self.username_input.setPlaceholderText("Invalid Username!")
            self.password_input.setPlaceholderText("Invalid Password!")

    # Add a button with an icon
    def add_main_button(self, layout, text, icon_path, callback, style):

        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def admin_function(self):
        """Enter admin page"""
        if "admin" in self.pages:
            self.right_stack.setCurrentWidget(self.pages["admin"])

    # Create setting page
    def create_setting_page(self):
        """Create setting page with buttons placed in the upper middle area."""
        logger.info("Create setting page")
        page = QWidget()
        layout = QVBoxLayout()

        # Add top space to push buttons slightly upwards
        layout.addItem(QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Create three buttons
        self.camera_button = QPushButton("Camera Setting", self)
        self.camera_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.camera_button.clicked.connect(self.camera_setting_function)

        self.gps_button = QPushButton("GPS Setting", self)
        self.gps_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gps_button.clicked.connect(self.gps_setting_function)

        self.imu_button = QPushButton("IMU Setting", self)
        self.imu_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.imu_button.clicked.connect(self.imu_setting_function)

        # Arrange buttons in the upper middle with some spacing
        layout.addWidget(self.camera_button, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.gps_button, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.imu_button, alignment=Qt.AlignCenter)

        # Add bottom stretch to keep layout balanced
        layout.addItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        page.setLayout(layout)
        
        return page

    def add_setting_button(self, layout, text, icon_path, callback, style):

        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        pass
    
    def get_available_cameras(self):
        """
        示例：返回可用的相机列表。
        实际应用中，请替换为真实的相机检测逻辑。
        """
        # 例如：假设系统中有 2 个相机
        return [0, 1]
    
    def add_camera_setting_button(self, layout, text, icon_path, callback, style):
        
        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        pass
    
    def add_gps_setting_button(self, layout, text, icon_path, callback, style):
        
        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        pass

    def add_imu_setting_button(self, layout, text, icon_path, callback, style):
        
        button = QPushButton(f" {text}", self)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        layout.addWidget(button)
        pass

    def admin_function(self):
        print("Admin button clicked!")

    def start_function(self):
        print("START button clicked!")
        self.right_stack.setCurrentWidget(self.pages["start"])

    def setting_function(self):
        """切换到 Setting 页面"""
        logger.info(f"join setting page")
        self.right_stack.setCurrentWidget(self.pages["setting"])

    def camera_setting_function(self):
        """切换到 Camera Setting 页面"""
        logger.info(f"join camera setting page")
        self.right_stack.setCurrentWidget(self.pages["camera_setting"])

    def gps_setting_function(self):
        logger.info(f"join gps setting page")
        self.right_stack.setCurrentWidget(self.pages["gps_setting"])
    
    def imu_setting_function(self):
        logger.info(f"join imu setting page")
        self.right_stack.setCurrentWidget(self.pages['imu_setting'])
    
    def map_function(self):
        """点击 DataMap 按钮后，显示 DataMap 页面"""
        print("DataMap button clicked! 显示卫星地图")
        self.right_stack.setCurrentWidget(self.pages["map"])

    def data_function(self):
        print("Data button clicked!")
        self.right_stack.setCurrentWidget(self.pages["data"])

    def data_process(self):
        logger.info(f"DataProcess button clicked!")
        self.right_stack.setCurrentWidget(self.pages["process"])

    def logout_function(self):
        print("Logout button clicked!")
        # 禁用除 admin 以外的所有按钮（或者自定义禁用逻辑）
        self.disable_buttons()

        # 清空登录输入框，并重置提示
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setPlaceholderText("Enter Username")
        self.password_input.setPlaceholderText("Enter Password")

        # 切换到 admin 登录页面
        self.right_stack.setCurrentWidget(self.pages["admin"])
        
    def disable_buttons(self):
        """disable all the buttons on the left except admin"""
        for key, button in self.buttons.items():
            if key != "admin":
                button.setEnabled(False)

    def enable_buttons(self):
        """enable all the button on the left"""
        for button in self.buttons.values():
            button.setEnabled(True)


    def goto_default(self):
        self.right_stack.setCurrentWidget(self.pages["default"])  
    
    def goto_setting(self):
        self.right_stack.setCurrentWidget(self.pages["setting"])  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgroSenseApp()
    window.show()
    sys.exit(app.exec_())
