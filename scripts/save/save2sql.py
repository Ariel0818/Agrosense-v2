import sqlite3
import json
import os

class ImageDataDB:
    def __init__(self, db_path="data/analysis.db"):
        """
        初始化 SQLite 数据库连接，并创建表（如果尚未创建）。
        """
        self.db_path = db_path
        self.conn    = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor  = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        创建数据库表（如果尚未创建）。
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rgb_path TEXT,
            depth_path TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL
        )
        ''')
        self.conn.commit()

    def insert_data(self, json_data):
        """
        插入单条 AI 处理后的 JSON 数据到数据库。
        :param json_data: 字典格式的数据
        """
        self.cursor.execute('''
        INSERT INTO image_data (timestamp, rgb_path, depth_path, latitude, longitude, altitude)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            json_data["timestamp"],
            json_data["rgb_path"],
            json_data["depth_path"],
            json_data["latitude"],
            json_data["longitude"],
            json_data["altitude"]
        ))
        self.conn.commit()

    def insert_from_json_file(self, json_file):
        """
        读取 JSON 文件并批量插入数据。
        :param json_file: JSON 文件路径
        """
        if not os.path.exists(json_file):
            print(f"文件 {json_file} 不存在！")
            return

        with open(json_file, "r") as f:
            data = json.load(f)
            for entry in data:
                self.insert_data(entry)
        print(f"成功存入 JSON 文件: {json_file}")

    def fetch_all(self):
        """
        获取数据库中所有数据。
        :return: 所有数据的列表
        """
        self.cursor.execute("SELECT * FROM image_data")
        return self.cursor.fetchall()

    def fetch_latest(self, limit=5):
        """
        获取最新的 N 条数据。
        :param limit: 获取的数据条数
        :return: 最新的数据
        """
        self.cursor.execute("SELECT * FROM image_data ORDER BY timestamp DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def fetch_by_gps_range(self, lat_min, lat_max, lon_min, lon_max):
        """
        根据 GPS 坐标范围查询数据。
        :param lat_min: 最小纬度
        :param lat_max: 最大纬度
        :param lon_min: 最小经度
        :param lon_max: 最大经度
        :return: 在指定范围内的数据
        """
        self.cursor.execute('''
        SELECT * FROM image_data 
        WHERE latitude BETWEEN ? AND ? 
        AND longitude BETWEEN ? AND ?
        ''', (lat_min, lat_max, lon_min, lon_max))
        return self.cursor.fetchall()

    def close(self):
        """
        关闭数据库连接。
        """
        self.conn.close()
