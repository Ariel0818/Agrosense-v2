import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

class DataProcess(QWidget):
    def __init__(self, directory=None, parent=None):
        """
        :param directory: 要显示的文件夹路径，默认为 "~/Documents/Agrosense/data/images"
        :param parent: 父控件
        """
        super().__init__(parent)
        # 如果没有传入目录，则使用默认目录（展开 ~）
        self.directory = directory or os.path.expanduser("~/Documents/Agrosense/data/images")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("Data Process", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 列表控件，用于显示目录中的内容
        self.listWidget = QListWidget(self)
        # 设置多选模式
        self.listWidget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.listWidget)
        
        # 填充列表：只显示目录（例如 depth, depth1, rgb, rgb1）
        self.populateList()
        
        # 处理选项：使用复选框
        options_layout = QHBoxLayout()
        self.checkboxDensity = QCheckBox("density", self)
        self.checkboxHeight = QCheckBox("height", self)
        self.checkboxFruitCount = QCheckBox("fruit count", self)
        self.checkboxTreeNumber = QCheckBox("treenumber", self)
        options_layout.addWidget(self.checkboxDensity)
        options_layout.addWidget(self.checkboxHeight)
        options_layout.addWidget(self.checkboxFruitCount)
        options_layout.addWidget(self.checkboxTreeNumber)
        layout.addLayout(options_layout)
        
        # 添加 Process 按钮
        self.processButton = QPushButton("Process", self)
        self.processButton.clicked.connect(self.processData)
        layout.addWidget(self.processButton)
        
        self.setLayout(layout)

    def populateList(self):
        """
        填充列表控件，显示 self.directory 目录下的内容（这里只显示目录）
        """
        if not os.path.exists(self.directory):
            QMessageBox.critical(self, "Error", f"Directory does not exist:\n{self.directory}")
            return
        
        # 获取目录下的所有内容，并过滤只显示目录（如果你希望显示文件，删除过滤条件）
        items = os.listdir(self.directory)
        items = [item for item in items if os.path.isdir(os.path.join(self.directory, item))]
        self.listWidget.clear()
        for item in items:
            list_item = QListWidgetItem(item, self.listWidget)
            self.listWidget.addItem(list_item)

    def processData(self):
        """
        当用户点击 Process 按钮时，获取选中的目录和处理选项，然后执行相应的处理操作。
        示例中通过弹窗和打印输出显示选中的信息。
        """
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No selection", "Please select at least one item.")
            return
        
        selected_names = [item.text() for item in selected_items]
        options = {
            "density": self.checkboxDensity.isChecked(),
            "height": self.checkboxHeight.isChecked(),
            "fruit count": self.checkboxFruitCount.isChecked(),
            "treenumber": self.checkboxTreeNumber.isChecked()
        }
        
        # 模拟处理：打印选中结果和选项，并弹出信息框
        print("Selected items:", selected_names)
        print("Processing options:", options)
        QMessageBox.information(self, "Processing",
                                f"Processing {selected_names}\nwith options {options}")
        # 在这里，你可以根据选中内容和选项调用具体的处理函数，比如：
        # process_files(selected_names, options)
