import numpy as np
import cv2
import struct
import time
from socket import *
from camera import Camera

class Server:

    def __init__(self, addr):
        self.addr = addr
        self.camera = Camera()


    def send(self):
        s = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        cap = self.camera.open_camera()

        while True:
            fps = self.camera.get_fps(cap)
            resolution = self.camera.get_resolution(cap)
            frame = self.camera.get_frame(cap)

            # 发送视频帧率
            s.sendto(struct.pack("i", int(fps)), self.addr)

            # 发送视频的分辨率
            s.sendto(struct.pack("<ff", resolution[0], resolution[1]), self.addr)

            # 将数据打包发送
            s.sendto(frame, self.addr)
            print(f'正在发送数据，大小:{len(frame)} Byte')


if __name__ == "__main__":
    server = Server(('172.16.57.95', 8888))
    server.send()