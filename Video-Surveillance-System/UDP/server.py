import struct
import time
import csv
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
            img_start = time.time()    # 计算获取图片和编码时间
            fps = self.camera.get_fps(cap)
            resolution = self.camera.get_resolution(cap)
            frame = self.camera.get_frame(cap)
            img_end = time.time()    # 计算获取图片和编码时间

            send_start = time.time()    # 计算发送图片时间
            # 发送视频帧率
            s.sendto(struct.pack("i", int(fps)), self.addr)

            # 发送视频的分辨率
            s.sendto(struct.pack("<ff", resolution[0], resolution[1]), self.addr)

            # 将数据打包发送
            s.sendto(frame, self.addr)
            send_end = time.time()    # 计算发送图片时间

            img_delay = img_end - img_start
            pack_delay = send_end - send_start
            send_delay = send_end - img_start
            print(f'正在发送数据，大小:{len(frame)} Byte')
            print(f'总发送时延：{send_delay:.3f}获取图片时延：{img_delay:.3f}；打包发送时延{pack_delay:.3f}')

            delay = [round(send_delay, 3), round(img_delay, 3), round(pack_delay, 3)]
            with open('UDP_delay.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(delay)


if __name__ == "__main__":
    # server = Server(('172.16.57.95', 8888))
    server = Server(('192.168.43.246', 8888))
    server.send()