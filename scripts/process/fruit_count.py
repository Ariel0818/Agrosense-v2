class FruitCount:
    def __init__(self, data_path):
        self.data_path = data_path

    def process(self):
        # 示例：统计果实数量，返回一个整数值
        fruit_count = random.randint(5, 20)
        print(f"Fruit count processed: {fruit_count}")
        return fruit_count