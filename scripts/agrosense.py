import sys
from PyQt5.QtWidgets import QApplication
from manager.task_manager import TaskManager
from visualizations.gui import AgroSenseApp

def start_agrosense():
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    
    device_id_pairs    = [('033422071163',), ('250122075706',)]
    width, height, fps = 480, 640, 30
    camera_parameters = {
        '033422071163': {'exposure': 8,  'gain': 1},
        '250122075706': {'exposure': 10, 'gain': 2},
    }
    # device_id_pairs = [('033422071163',),]
    camera_parameters = {'033422071163': {'exposure': 8, 'gain': 1}}
    # 创建 TaskManager 实例（任务管理器）
    taskManager = TaskManager(device_id_pairs, camera_parameters, width, height, fps)
    
    # 将任务管理器实例传递给主 UI 类 AgroSenseApp
    main_window = AgroSenseApp(taskManager)
    
    # 显示主窗口
    main_window.show()
    
    # 进入应用程序的事件循环
    sys.exit(app.exec_())

if __name__ == '__main__':
    start_agrosense()
