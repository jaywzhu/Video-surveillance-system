import struct
import time
import csv
import threading
from socket import *
from camera import Camera

class Server:
    def __init__(self, udp_address, tcp_address):
        self.udp_address = udp_address
        self.tcp_address = tcp_address
        self.camera = Camera()
        self.cap = None

    def send(self):
        '''
        发送视频流
        :return:
        '''
        s = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        self.cap = self.camera.open_camera()

        while True:
            img_start = time.time()    # 计算获取图片和编码时间
            # 从摄像头中获取帧率、分辨率、图像质量和一帧视频
            camera_fps = self.camera.get_fps(self.cap)
            resolution = self.camera.get_resolution(self.cap)
            quality = self.camera.get_quality()
            frame = self.camera.get_frame(self.cap)
            img_end = time.time()    # 计算获取图片和编码时间

            send_start = time.time()    # 计算发送图片时间
            # 发送摄像头帧率
            s.sendto(struct.pack("i", int(camera_fps)), self.udp_address)

            # 发送视频的分辨率
            s.sendto(struct.pack("<ff", resolution[0], resolution[1]), self.udp_address)

            # 发送图像编码质量
            s.sendto(struct.pack("i", int(quality)), self.udp_address)

            # 将数据打包发送,如果图片太大，降低分辨率再发送
            try:
                s.sendto(frame, self.udp_address)
            except OSError:
                self.camera.set_quality(self.cap, 0)
                continue
            send_end = time.time()    # 计算发送图片时间

            img_delay = img_end - img_start
            pack_delay = send_end - send_start
            send_delay = send_end - img_start
            # print(f'正在发送数据，大小:{len(frame)} Byte')
            # print(f'总发送时延：{send_delay:.3f}获取图片时延：{img_delay:.3f}；打包发送时延{pack_delay:.3f}')

            delay = [round(send_delay, 3), round(img_delay, 3), round(pack_delay, 3)]
            with open('UDP_delay.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(delay)

    def rec_message(self):
        rec_sock = socket(AF_INET, SOCK_STREAM)
        rec_sock.connect(self.tcp_address)
        print('连接成功')
        while True:
            message = rec_sock.recv(16)
            message = message.decode()
            if message == 'r':
                new_cap = self.camera.set_resolution(self.cap, 1)
                self.cap = new_cap
            if message == 't':
                new_cap = self.camera.set_resolution(self.cap, 0)
                self.cap = new_cap
            if message == 'o':
                self.camera.set_quality(self.cap, 1)
            if message == 'p':
                self.camera.set_quality(self.cap, 0)
            print(message)

if __name__ == "__main__":
    udp_address = ('172.16.57.95', 8888)
    tcp_address = ('172.16.57.95', 7777)
    server = Server(udp_address, tcp_address)
    # server = Server(('192.168.43.246', 8888))
    rec_thread = threading.Thread(target=server.rec_message)
    rec_thread.start()
    server.send()