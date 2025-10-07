## Feb 4, 2025:
Use the 013 right filtered images, with a filter parameter of 4.5, to (==dataset1, total 997 images==)train the model to detect the trunk; the result is saved in train2. (Using dataset1)

## Feb 18, 2025:
Apply weight from train2 to the ==013 left== filtered image (4.5)  and count the correctly detected trunk. result very bad. 

label more data from 013 left (filtered image 5.5) and train based on =="train2"== weight.

Combine the dataset1(13R) and 13L, to dataset2. 
13L total 1148 images
==dataset2: a total of 2145 images. (13 L and 13 R)==

training result saved in ==train3==

use the train3 best.pt predict ==014 left==, the result saved in ==predict==, actually quite good, but the bounding box are too much, can't be for one image there is only one trunk detected, sometimes the branches are also detected. need to find a method to keep only the bounding box we want. I don't think improving the confidence score will help because some unnecessary bounding boxes are high. thinking about setting a limitation for the bounding box location.


## Linux commend
mv valid/ /media/dataset2
rm -r dataset2
mkdir 013

## Feb 20, 2025
complie the model prediction reuslt, 014, 015, 016. into ==Result.xlsx==
the chart ==trunk central detected?== means when the tree is in the middle of the image, if the tree trunk is detected.

014 L: predict 
014 R: predict2
015 L: predict3
015 R: predict4
016 L: predict5
016 R: predict6

## Feb 21, 2025

001 L:




after finish all the processing, need to select the images that are not seceseccuslly detected when the bounding box is in the central of the image: add the gap information
Problem: the tree trunk detection is not that clean: there can be many bounding box for one tree, some times the tree banch is also detected, and also the some banch on the ground.

the logistic should be:

1. object detection, only keep the bounding box located at the ground area. increase the confident score. 

2. at the same time save the central point of the image depth value. 

if the trunk is countinous appear follow the direction of the car moving, collect as one tree. at the same time count the central area of the image

## 3.19.2025
try to use ai method to seperate everything.
试图使用mmdetection，但是mmcv版本安装不对，mmcvrc4总是安装不上，先暂时放弃了

## 3.20.2025
感觉脑子乱乱的，有点不知道现在该做什么
现在有三种方法：
1. 在trunk detection的基础上进行基础的image processing method，看看能不能把两颗树分开。
2. 重新训练网络，进行分割。直接分割出树干和canopy,但标注数据集非常耗时间，想用sam自动标注数据集但是效果不好。于是手动在roboflow标注，因为我的labelme不好使，老是闪退。之后的模型还是在考虑使用mmdetection（如果可以的话），或者就还是用yolo最快得到结果 (rtwnet)
3. 不做分割了，直接把图片输出来做classification，判断一张图片上有几棵树，训练这个。(restnet)

## 4.9.2025
从会议回来了，更不知道该怎么做了，尤其是距离回国只有两个星期，有点不知道改从何做起。
上次和老板说过之后他说要多采数据，根据数据类型来看到底哪个方法最合适。所以现在和老板说了买新的相机zen x，已经拿到了，另外还有想买一个新的jetson agx orin，这个还在买。目前就是不知道改做些什么

问了一下chatgpt，他真的比老板好用，结合他的意见，准备现在在等采数据的同时先把三个方法都显得到一个初步的结果：

---

## 🧭 一、你现在处于的阶段：**“选路线 + 初步验证”**

老板说“多采数据、看数据决定方法”，这句话其实给你定了基调：

> **优先任务：采数据 ➜ 尝试不同模型/方法 ➜ 看结果选路径**

---

## ✅ 二、你的三个方法怎么选？我来给你一点建议：

### ### ✨方法1：Image Processing 分开两棵树
- ✅ **优点**：不需要标注、马上可以做；验证简单直观。
- ⚠️ **缺点**：树之间重叠多、背景复杂时效果差。

📌 **建议**：这个可以作为 baseline 马上试，不要花太久时间。如果效果太差，就用它作为对比，不继续投入。

---

### ### ✨方法2：做分割（RTWNet / YOLO / MMDetection）
- ✅ **优点**：精度高，可扩展性强（比如后续 canopy 分割、体积估计都能用）。
- ⚠️ **缺点**：标注工作量大；SAM自动标注又不够好。

📌 **建议**：
- 你已经在手动标注，**先标注少量图片（50张左右）做实验集**。
- **先用 YOLO 训练分割模型快速出结果**（MMDetection可以之后再用，先快速验证）
- 等你买到 Orin，**再考虑上 RTWNet 或多模型 ensemble。**

---

### ### ✨方法3：分类图片中的树数量（ResNet）
- ✅ **优点**：标签简单、训练快；分类任务鲁棒性好。
- ⚠️ **缺点**：只能得到“几棵树”而不是具体位置。

📌 **建议**：这个是个“Plan B”，**适合你时间紧或数据质量差的情况**。你可以：
- 利用现有图像按树的数量分几类（1颗、2颗...）
- 快速训练一个 ResNet，**大概一天就能验证完效果**

---

## 🚦三、当前阶段推荐的路线（鱼鱼专属任务清单！）

| 优先级 | 任务 | 时间预估 | 说明 |
|--------|------|----------|------|
| ⭐⭐⭐ | 使用新 ZED X 相机采集一批高质量数据 | 1–2天 | 带 IMU + 深度图 + RGB，能支持后续任何方法 |
| ⭐⭐ | 方法1：试试图像处理分离两棵树 | 1天 | 马上能做，验证可行性 |
| ⭐⭐ | 方法3：做一个图像分类模型（树的数量） | 1–2天 | 标签轻，快速测试网络效果 |
| ⭐⭐ | 方法2：先标注50张图，跑 YOLO 分割 | 2–3天 | 作为主力方向初步测试 |
| ⭐ | 研究 RTWNet/MMDetection 细节 | 等模型效果好再深入 | 暂缓，先验证再深入开发 |


## 🌱 总结一句话

**你现在的重点是：采好数据 ➜ 快速测试不同方法的初步效果 ➜ 再决定深挖哪个方向。**

你已经做得很好了鱼鱼，不用给自己太大压力！现在就从简单的任务入手（比如跑通一个分割或者分类模型），做出一点进展，你的方向感就会慢慢回来！我们随时可以调整方向，我在呢 💪🐟

	---

所以结合他说的我准备先把paper框架搭好，准备先用图像处理方式分割两颗树看看 （这个是基于树干检测的）

## 4.14.2025
trunk+ 数gap方法可以。数gap是通过计算指定范围内 非黑色像素占比全部像素的大小获得的。黑色占比越多，说明此处是一个gap的可能性越大。

trunk detection 得到bounding box之后，只留下图片靠近地面部分的boundingbox， 在这之后选择confident score top2 的两个留下

## 4.16.2025

path 生成 yolo label保存的路径

1. 相机拍照一张
2. yolo检测trunk得到label
3. clean label： 
	去掉xcenter太大的 -> 只留下地面上的bounding box 
	去掉同一水平线的, 如果在同一水平线上留下x最小的那个（靠近地面的那个） -> 影响后续判断，一块地上垂直方向只能有一个 bbx

理想情况是一张图上只有一个bounding box， 但也有特殊情况比如 214.jpg很难弄， 246， 256

3.  
	去掉bounding box太小的bbx


## 5.24.2025
一些复杂情况以及解决方法： 
1. 连续错误的detection，比如在地面上连续多个图片识别到了影子。  --> 检测画面中心ratio，可以过滤掉一些情况。
2. 
































