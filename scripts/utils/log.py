import logging

class LoggerManager:
    def __init__(self, name=__name__, level=logging.DEBUG):
        """
        初始化 Logger
        :param name: 日志名称（默认使用 __name__）
        :param level: 日志级别（默认 DEBUG）
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 防止重复添加多个处理器
        if not self.logger.hasHandlers():
            # 创建日志格式
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)

            # 添加处理器到 Logger
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """返回 Logger 实例"""
        return self.logger

if __name__ == "__main__":
    logger = LoggerManager().get_logger()
    logger.info("Logger 正常工作")