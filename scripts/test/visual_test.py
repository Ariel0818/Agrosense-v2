import sqlite3
import matplotlib.pyplot as plt

# 连接数据库
conn = sqlite3.connect("data/combined_data.db")
cursor = conn.cursor()

# 查询 GPS 数据
cursor.execute("SELECT latitude, longitude FROM combined_data")
gps_data = cursor.fetchall()

# 分离经纬度
latitudes = [row[0] for row in gps_data]
longitudes = [row[1] for row in gps_data]

# 绘制 GPS 点的分布
plt.figure(figsize=(10, 6))
plt.scatter(longitudes, latitudes, c='blue', alpha=0.5, label="GPS Points")
plt.title("GPS Data Distribution")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid()
plt.show()

# 关闭数据库连接
conn.close()
