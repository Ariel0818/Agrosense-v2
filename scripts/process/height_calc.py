class HeightCalculate:
    def __init__(self, data_path):
        self.data_path = data_path

    def process(self):
        # 示例：计算作物高度，返回一个示例值（单位：米）
        height = round(random.uniform(1.0, 3.0), 2)
        print(f"Height processed: {height} m")
        return height