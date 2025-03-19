class DensityClassification:
    def __init__(self, data_path):
        self.data_path = data_path

    def process(self):
        # 示例：根据数据路径计算密度，这里返回一个随机示例结果
        density_level = random.choice(["low", "medium", "high"])
        print(f"Density processed: {density_level}")
        return density_level