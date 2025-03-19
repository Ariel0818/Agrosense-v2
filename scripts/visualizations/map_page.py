import os
import json
import folium
import sqlite3
import random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from folium.plugins import Draw

def create_database(db_path="data/datapoints.db"):
    """
    创建数据库和数据表（如果不存在）。
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datapoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT,              -- 如 "2023-01" 或 "2023-02"
            timestamp TEXT,          -- 采集时间戳，例如 "2023-01-15T12:00:00"
            latitude REAL,           -- 纬度
            longitude REAL,          -- 经度
            popup TEXT,              -- 弹出信息，例如 "采集时间: 2023-01-15T12:00:00"
            fillColor TEXT,          -- 图标颜色，例如 "green"
            fillOpacity REAL,        -- 透明度，例如 0.8
            radius REAL              -- 半径，例如 6
        );
    """)
    conn.commit()
    conn.close()

def generate_datapoints(center_lat, center_lon):
    """
    模拟生成数据点，返回格式为：
    {
      "2023-01": { "type": "FeatureCollection", "features": [...] },
      "2023-02": { "type": "FeatureCollection", "features": [...] }
    }
    每个月生成20个随机分布的数据点，采集时间为该月份的随机日期。
    """
    datapoints = {
        "2023-01": {"type": "FeatureCollection", "features": []},
        "2023-02": {"type": "FeatureCollection", "features": []}
    }
    for month in ["2023-01", "2023-02"]:
        for i in range(2000):
            lat = center_lat + random.uniform(-0.01, 0.01)
            lon = center_lon + random.uniform(-0.01, 0.01)
            day = random.randint(1, 28)
            timestamp = f"{month}-{day:02d}T12:00:00"
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]  # GeoJSON 坐标格式：[经度, 纬度]
                },
                "properties": {
                    "times": [timestamp],
                    "popup": f"采集时间: {timestamp}",
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": "green",
                        "fillOpacity": 0.8,
                        "stroke": "true",
                        "radius": 6
                    }
                }
            }
            datapoints[month]["features"].append(feature)
    return datapoints

def populate_database(db_path, center_lat, center_lon):
    """
    调用 generate_datapoints() 生成模拟数据，然后将数据逐条插入到数据库中。
    """
    # 先创建数据库和数据表
    create_database(db_path)
    data = generate_datapoints(center_lat, center_lon)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for month, fc in data.items():
        for feature in fc["features"]:
            timestamp = feature["properties"]["times"][0]
            # 注意：GeoJSON 格式中，coordinates 格式为 [lon, lat]
            lon, lat = feature["geometry"]["coordinates"]
            popup = feature["properties"]["popup"]
            fillColor = feature["properties"]["iconstyle"]["fillColor"]
            fillOpacity = feature["properties"]["iconstyle"]["fillOpacity"]
            radius = feature["properties"]["iconstyle"]["radius"]
            cursor.execute("""
                INSERT INTO datapoints (month, timestamp, latitude, longitude, popup, fillColor, fillOpacity, radius)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (month, timestamp, lat, lon, popup, fillColor, fillOpacity, radius))
    conn.commit()
    conn.close()
    print("数据库已填充模拟数据。")

def fetch_datapoints_from_db(db_path):
    """
    从数据库中读取数据点，并组织成前端需要的格式：
    {
      "2023-01": { "type": "FeatureCollection", "features": [...] },
      "2023-02": { "type": "FeatureCollection", "features": [...] }
    }
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
    SELECT month, timestamp, latitude, longitude, popup, fillColor, fillOpacity, radius
    FROM datapoints;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    datapoints = {}
    for row in rows:
        month, timestamp, lat, lon, popup, fillColor, fillOpacity, radius = row
        if month not in datapoints:
            datapoints[month] = {"type": "FeatureCollection", "features": []}
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "times": [timestamp],
                "popup": popup,
                "icon": "circle",
                "iconstyle": {
                    "fillColor": fillColor,
                    "fillOpacity": fillOpacity,
                    "stroke": "true",
                    "radius": radius
                }
            }
        }
        datapoints[month]["features"].append(feature)
    return datapoints

class DataMapPage(QWidget):
    # 定义一个信号，当点击 Back 按钮时发射（可用于页面导航）
    backClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 使用垂直布局放置地图视图
        layout = QVBoxLayout(self)
        self.map_view = QWebEngineView(self)
        self.map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.map_view)
        self.setLayout(layout)
        # 初始加载地图
        self.updateMap()

    def updateMap(self):
        """生成地图文件，并加载到 QWebEngineView 中"""
        map_path = self.generateMap()
        local_url = QUrl.fromLocalFile(os.path.abspath(map_path))
        self.map_view.setUrl(local_url)
        print(f"成功加载卫星地图: {local_url.toString()}")

    def generateMap(self):
        """生成带有卫星图层、绘图工具以及下拉框选择的地图，并嵌入从数据库读取的数据点"""
        map_path = "satellite_map.html"
        center_lat, center_lon = 26.464396, -81.443663
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, max_zoom=21)
        
        # 添加卫星图层（Esri 和 Google）
        folium.TileLayer('Esri.WorldImagery').add_to(m)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google",
            name="Google Satellite",
            overlay=False,
            control=True,
            max_zoom=21
        ).add_to(m)
        folium.LayerControl().add_to(m)
        
        # 从数据库中读取数据点（数据库文件路径为 "data/datapoints.db"）
        db_path = "data/datapoints.db"
        datapoints = fetch_datapoints_from_db(db_path)
        
        # 添加 Draw 插件，保留左侧绘图工具（仅 polygon 与 circleMarker），关闭底部工具栏
        draw = Draw(
            export=False,
            draw_options={
                'polyline': False,
                'polygon': True,
                'circle': False,
                'marker': False,
                'circlemarker': True,
                'rectangle': False,
            },
            edit_options={
                'edit': True,
                'remove': True,
            }
        )
        draw.add_to(m)
        
        # 添加下拉框工具栏（HTML 部分）
        custom_toolbar = """
        <div id="custom-toolbar" style="position: fixed; top: 10px; right: 10px; z-index: 9999;
            background: white; padding: 10px; border: 2px solid gray;">
            <label for="date-select">选择日期 (年月):</label>
            <select id="date-select">
              <option value="2023-01">2023-01</option>
              <option value="2023-02">2023-02</option>
              <option value="all">全部</option>
            </select>
        </div>
        """
        m.get_root().html.add_child(folium.Element(custom_toolbar))
        
        # 将查询到的数据点存入全局变量 window.datapoints
        store_datapoints_js = f"""
        <script>
        window.datapoints = {json.dumps(datapoints)};
        </script>
        """
        m.get_root().html.add_child(folium.Element(store_datapoints_js))
        
        # 自定义 JavaScript 部分：包装在 window.onload 中
        custom_js = f"""
        <script>
        window.addEventListener('load', function() {{
            var map = window["{m.get_name()}"];
            
            function addMarkersForMonth(selected) {{
                if (window.markerLayer) {{
                    map.removeLayer(window.markerLayer);
                }}
                window.markerLayer = L.layerGroup();
                if (selected === "all") {{
                    Object.keys(window.datapoints).forEach(function(monthKey) {{
                        if(window.datapoints[monthKey] && window.datapoints[monthKey].features) {{
                            window.datapoints[monthKey].features.forEach(function(feature) {{
                                var coords = feature.geometry.coordinates;
                                var marker = L.circleMarker([coords[1], coords[0]], {{
                                    color: feature.properties.iconstyle.fillColor,
                                    fillOpacity: feature.properties.iconstyle.fillOpacity,
                                    radius: feature.properties.iconstyle.radius
                                }});
                                marker.bindPopup(feature.properties.popup);
                                marker.on('contextmenu', function(e) {{
                                    map.removeLayer(marker);
                                }});
                                marker.addTo(window.markerLayer);
                            }});
                        }}
                    }});
                }} else {{
                    if(window.datapoints[selected] && window.datapoints[selected].features) {{
                        window.datapoints[selected].features.forEach(function(feature) {{
                            var coords = feature.geometry.coordinates;
                            var marker = L.circleMarker([coords[1], coords[0]], {{
                                color: feature.properties.iconstyle.fillColor,
                                fillOpacity: feature.properties.iconstyle.fillOpacity,
                                radius: feature.properties.iconstyle.radius
                            }});
                            marker.bindPopup(feature.properties.popup);
                            marker.on('contextmenu', function(e) {{
                                map.removeLayer(marker);
                            }});
                            marker.addTo(window.markerLayer);
                        }});
                    }} else {{
                        console.log("No data for selected month: " + selected);
                    }}
                }}
                window.markerLayer.addTo(map);
            }}
            
            document.getElementById('date-select').addEventListener('change', function(e) {{
                var selected = e.target.value;
                console.log("Selected month: " + selected);
                addMarkersForMonth(selected);
            }});
            
            addMarkersForMonth(document.getElementById('date-select').value);
            
            map.on('draw:created', function (e) {{
                var layer = e.layer;
                layer.on('contextmenu', function(e) {{
                    map.removeLayer(layer);
                }});
                layer.addTo(map);
            }});
        }});
        </script>
        """
        m.get_root().html.add_child(folium.Element(custom_js))
        
        m.save(map_path)
        print(f"地图生成成功: {os.path.abspath(map_path)}")
        return map_path

if __name__ == '__main__':
    db_path = "data/datapoints.db"
    center_lat, center_lon = 26.464396, -81.443663
    # 填充数据库：将模拟数据插入数据库
    populate_database(db_path, center_lat, center_lon)
    # 创建并显示地图页面
    m_page = DataMapPage()
    m_page.updateMap()
