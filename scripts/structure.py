import matplotlib.pyplot as plt
import networkx as nx

# 创建有向图
G = nx.DiGraph()

# 添加节点（系统组成部分）
nodes = {
    "UI 控制系统": (0, 6),
    "深度学习模型 (树高+密度计算)": (0, 4.5),
    "数据存储与可视化": (0, 3),
    "上位机 (PC / 工业计算机)": (-2, 4.5),
    "下位机 (嵌入式控制器)": (-2, 3),
    "相机 (图像采集)": (-4, 5.5),
    "GPS + IMU (定位系统)": (-4, 3.5),
    "喷嘴控制 (执行器)": (-4, 2),
    "流量计 (喷雾监测)": (-4, 0.5),
}

# 添加节点到图
G.add_nodes_from(nodes.keys())

# 添加边（数据流）
edges = [
    ("UI 控制系统", "上位机 (PC / 工业计算机)"),
    ("上位机 (PC / 工业计算机)", "深度学习模型 (树高+密度计算)"),
    ("深度学习模型 (树高+密度计算)", "上位机 (PC / 工业计算机)"),
    ("上位机 (PC / 工业计算机)", "下位机 (嵌入式控制器)"),
    ("相机 (图像采集)", "深度学习模型 (树高+密度计算)"),
    ("GPS + IMU (定位系统)", "下位机 (嵌入式控制器)"),
    ("下位机 (嵌入式控制器)", "喷嘴控制 (执行器)"),
    ("喷嘴控制 (执行器)", "流量计 (喷雾监测)"),
    ("流量计 (喷雾监测)", "上位机 (PC / 工业计算机)"),
    ("上位机 (PC / 工业计算机)", "数据存储与可视化"),
]

# 添加边到图
G.add_edges_from(edges)

# 设定节点位置
pos = nodes

# 绘制图形
plt.figure(figsize=(10, 7))
nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=3000, font_size=9, font_weight="bold", arrows=True)

# 显示架构图
plt.title("喷雾车智能控制系统架构图")
plt.show()
