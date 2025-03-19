import sqlite3
import os

def create_db(db_path="data/datapoints.db"):
    # 如果目录不存在，则创建目录
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接到数据库（如果不存在，则会自动创建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建数据表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datapoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,              -- 存储月份信息，如 "2023-01" 或 "2023-02"
        timestamp TEXT,          -- 存储采集时间戳，如 "2023-01-15T12:00:00"
        latitude REAL,           -- 纬度
        longitude REAL,          -- 经度
        popup TEXT,              -- 弹出信息，如 "采集时间: 2023-01-15T12:00:00"
        fillColor TEXT,          -- 图标填充颜色，例如 "green"
        fillOpacity REAL,        -- 填充透明度，例如 0.8
        radius REAL              -- 图标半径，例如 6
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"数据库已创建并保存到 {os.path.abspath(db_path)}")

if __name__ == "__main__":
    create_db()
