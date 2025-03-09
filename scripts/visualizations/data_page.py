import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileSystemModel
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

class DataPage(QWidget):
    def __init__(self, directory=None, parent=None):
        """
        :param directory: 要显示的文件夹路径，默认为 "~/Documents/Agrosense/data"
        :param parent: 父控件
        """
        super().__init__(parent)
        # 如果没有传入目录，则使用默认目录（展开 ~）
        self.directory = directory or os.path.expanduser("~/Documents/Agrosense/data")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 创建 QFileSystemModel 用于读取文件系统内容
        self.model = QFileSystemModel(self)
        self.model.setRootPath(self.directory)  # 设置模型的根路径
        
        # 创建 QTreeView 用于显示模型内容
        self.treeView = QTreeView(self)
        self.treeView.setModel(self.model)
        # 设定根目录显示为指定目录
        self.treeView.setRootIndex(self.model.index(self.directory))
        # 可选：隐藏除文件名以外的其它列
        for col in range(1, self.model.columnCount()):
            self.treeView.hideColumn(col)
        
        # 连接双击信号，响应用户双击文件或目录的操作
        self.treeView.doubleClicked.connect(self.onDoubleClicked)
        
        layout.addWidget(self.treeView)
        self.setLayout(layout)

    def onDoubleClicked(self, index):
        """
        当用户双击树中某个项时调用
        如果是文件，则使用系统默认应用打开；如果是目录，则 QTreeView 会自动展开目录。
        """
        # 获取双击项对应的完整文件路径
        path = self.model.filePath(index)
        if os.path.isfile(path):
            # 如果是文件，则使用 QDesktopServices 打开该文件
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        # 如果是目录，则 QTreeView 会自动展开，无需额外操作
