from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt

class StartPage(QWidget):
    def __init__(self, taskManager, parent=None):
        super().__init__(parent)
        self.taskManager = taskManager
        self.initUI()
    
    def initUI(self):
        # 使用垂直布局排列按钮
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 创建“Start Data Collection”按钮
        self.dataCollectionButton = QPushButton("Start Data Collection", self)
        self.dataCollectionButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # 直接连接到类内的处理方法
        self.dataCollectionButton.clicked.connect(self.handleDataCollection)
        
        # 创建“Start RealTime”按钮
        self.realTimeButton = QPushButton("Start RealTime", self)
        self.realTimeButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.realTimeButton.clicked.connect(self.handleRealTime)
        
        # 将按钮添加到布局中
        layout.addWidget(self.dataCollectionButton)
        layout.addSpacing(20)  # 增加间距
        layout.addWidget(self.realTimeButton)
        
        self.setLayout(layout)
    
    def handleDataCollection(self):
        """
        开始数据采集的处理逻辑
        你可以在这里添加启动数据采集相关的代码
        """
        print("Starting data collection...")
        # 例如，弹出一个信息框
        QMessageBox.information(self, "Data Collection", "Data collection has been started!")
        # self.taskManager.dataCollectTask()
    
    def handleRealTime(self):
        """
        开始实时处理的处理逻辑
        你可以在这里添加启动实时处理相关的代码
        """
        print("Starting real-time processing...")
        # 例如，弹出一个信息框
        QMessageBox.information(self, "RealTime", "RealTime processing has been started!")

        # self.taskManager.realtime_proces_task()
