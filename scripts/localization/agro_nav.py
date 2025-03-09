import can
import struct  # 用于数据的解码

import serial
import struct
import time


class USB2Navigator:
    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.system_running = False

        # 存储接收到的数据
        self.position_lat = 0.0
        self.position_lon = 0.0
        self.velocity = 0.0
        self.acceleration = 0.0

        # 初始化连接
        self.connect()

    def connect(self):
        """连接 USB 虚拟串口"""
        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=1)
            print(f"Connected to USB on port {self.port} with baudrate {self.baudrate}")
        except serial.SerialException as e:
            print(f"Failed to connect to USB: {e}")
            self.ser = None

    def send_start_signal(self):
        """发送启动信号到 ESP32"""
        if self.ser:
            try:
                start_message = struct.pack("<B", 0x01)  # 0x01 表示启动信号
                self.ser.write(start_message)
                print("Start signal sent to ESP32")
            except serial.SerialException as e:
                print(f"Failed to send start signal: {e}")

    def send_stop_signal(self):
        """发送停止信号到 ESP32"""
        if self.ser:
            try:
                stop_message = struct.pack("<B", 0x00)  # 0x00 表示停止信号
                self.ser.write(stop_message)
                print("Stop signal sent to ESP32")
            except serial.SerialException as e:
                print(f"Failed to send stop signal: {e}")

    def receive_data(self):
        """接收来自 ESP32 的经纬度、速度和加速度数据"""
        if self.ser:
            try:
                # 读取数据帧（假设 ESP32 发送 9 字节数据帧：1 字节类型 + 8 字节数据）
                raw_data = self.ser.read(9)
                if len(raw_data) == 9:
                    data_type, data_payload = raw_data[0], raw_data[1:]
                    if data_type == 0x01:  # 0x01 表示经纬度数据
                        self.position_lat, self.position_lon = struct.unpack("<ff", data_payload)
                        print(f"Received latitude and longitude - Lat: {self.position_lat}, Lon: {self.position_lon}")
                    elif data_type == 0x02:  # 0x02 表示速度和加速度数据
                        self.velocity, self.acceleration = struct.unpack("<ff", data_payload)
                        print(f"Received velocity and acceleration - Vel: {self.velocity}, Acc: {self.acceleration}")
                else:
                    print("Incomplete data received")
            except serial.SerialException as e:
                print(f"Failed to receive data: {e}")

    def postion_calc(self):

        return x, y, z
    
    def velocity_calc(self):

        return vx,vy,vz
    def close(self):
        """关闭 USB 连接"""
        if self.ser:
            self.ser.close()
            print("USB connection closed.")


# 用法示例
if __name__ == "__main__":
    usb_navigator = USB2Navigator(port="/dev/ttyACM0", baudrate=115200)
    usb_navigator.send_start_signal()  # 发送启动信号

    # 模拟接收数据
    try:
        usb_navigator.system_running = True
        while usb_navigator.system_running:
            usb_navigator.receive_data()
            time.sleep(1)  # 模拟间隔，避免占用过多资源
    except KeyboardInterrupt:
        print("Exiting...")

    usb_navigator.send_stop_signal()  # 发送停止信号
    usb_navigator.close()
