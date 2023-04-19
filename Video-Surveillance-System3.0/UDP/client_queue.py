import queue

import numpy as np
import cv2
import datetime
import time
import threading
import struct
from database import Mysql
from queue import Queue
from socket import *


class Client:
    def __init__(self, udp_address, tcp_address):
        self.udp_address = udp_address
        self.tcp_address = tcp_address
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.img_queue = Queue(maxsize=100)
        self.video_queue = Queue(maxsize=100)
        self.out = cv2.VideoWriter('videoUDP66.avi', self.fourcc, 30, (1280, 720))
        self.mysql = Mysql('localhost', 'jaywzhu', 'xp349708', 'video')

    def rec_frame(self):
        '''
        接收发送端发送来的视频帧
        :return:
        '''
        s = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        s.bind(self.udp_address)

        while True:
            data = None
            try:
                # 获取相机帧率
                camera_fps, ret = s.recvfrom(4)
                camera_fps = str(struct.unpack("i", camera_fps)[0])

                # 获取分辨率
                resolution, ret = s.recvfrom(8)
                width, height = struct.unpack("<ff", resolution)
                resolution = [width, height]

                # 获取图像编码质量
                quality, ret = s.recvfrom(4)
                quality = str(struct.unpack("i", quality)[0])
                print(f'图像质量{quality}')

                # 解码视频
                data, ret = s.recvfrom(65535)
                receive_data = np.frombuffer(data, dtype='uint8')
                r_img = cv2.imdecode(receive_data, 1)

                # 写入队列
                if self.img_queue.qsize() < 100:
                    frame_data = [camera_fps, resolution, r_img, quality]
                    video_data = [camera_fps, resolution, r_img, quality]
                    print(self.img_queue.qsize())
                    self.img_queue.put(frame_data)
                    self.video_queue.put(video_data)
                else:
                    time.sleep(1)
            except:
                pass

    def get_frame_data(self):
        '''
        该函数返回图像队列的一帧图像
        :return:
        '''
        frame_data = self.img_queue.get()
        return frame_data

    def get_video_data(self):
        '''
        该函数返回视频队列的一帧图像
        :return:
        '''
        video_data = self.video_queue.get()
        return video_data

    def show_video(self):
        '''
        该函数用于显示视频流
        可以手动调节分辨率和图像质量
        “r”和 “t” 提高或降低分辨率 ；“o” 和 "p"提高或降低图像质量
        :return:
        '''
        fps = ''
        while True:
            try:
                frame_data = self.get_frame_data()
                resolution = frame_data[1]
                width = resolution[0]
                height = resolution[1]
                frame = frame_data[2]
                quality = frame_data[3]



                # 显示时间
                font = cv2.FONT_HERSHEY_SIMPLEX
                current_time = datetime.datetime.now()
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                frame = cv2.putText(frame, current_time, (0, 17), font, 0.8,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # 显示帧率
                frame = cv2.putText(frame, f'fps:{fps}', (int(width) - 85, 17), font, 0.8,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # # 显示分辨率
                # frame = cv2.putText(frame, f'resolution:{width}x{height}', (int(width) - 85, 17), font, 0.6,
                #                     (0, 255, 255), 2, cv2.LINE_AA)
                #
                # # 显示图像质量
                # frame = cv2.putText(frame, f'quality:{quality}', (int(width) - 85, 17), font, 0.6,
                #                     (0, 255, 255), 2, cv2.LINE_AA)

                # 显示视频
                cv2.namedWindow("client", cv2.WINDOW_AUTOSIZE)
                cv2.imshow('client', frame)

                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                # 按"r"和“t”键调节分辨率
                if key == ord('r'):
                    print('提高分辨率')
                    self.send_message('r')
                if key == ord('t'):
                    print('降低分辨率')
                    self.send_message('t')
                if key == ord('o'):
                    print('提高图片质量')
                    self.send_message('o')
                if key == ord('p'):
                    print('降低图片质量')
                    self.send_message('p')

            except:
                pass

    def record_video(self):
        '''
        该函数用于保存视频录像，初定为每个录像视频2分钟
        将录像信息保存在数据库
        :return:
        '''
        video_start = time.time()
        set_flag = True
        old_width = None
        while True:
            video_data = self.get_video_data()
            camera_fps = video_data[0]
            width = video_data[1][0]
            height = video_data[1][1]
            video = video_data[2]

            # 如果分辨率改变了，需要重新设置录像视频的参数
            if old_width != width:
                set_flag = True
                old_width = width
                self.video_queue = Queue(maxsize=100)
                continue

            now = datetime.datetime.now()
            formatted_time = now.strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'{formatted_time}.avi'
            # 重新设置录像视频参数
            if set_flag == True:
                self.out = cv2.VideoWriter(f'video_file/{filename}',
                                           self.fourcc, int(camera_fps), (int(width), int(height)))
                # 录像信息写入数据库
                date_time = now.strftime('%Y-%m-%d')
                sql = 'insert into video_info VALUES("厂区","材料","{}", "{}")'
                sql = sql.format(date_time, filename)
                self.mysql.excute_sql(sql)
                set_flag = False

            self.out.write(video)
            video_end = time.time()
            if video_end - video_start >= 100:  # 每隔两个分钟录制一个视频
                set_flag = False
                video_start = video_end

    def clear_queue(self, q):
        '''
        清空所给的队列中所有元素
        :param q:
        :return:
        '''
        size = q.qsize()
        for i in range(size):
            q.put()

    def init_tcp(self):
        '''
        该函数用于初始化建立tcp连接，传输控制信息
        :return:
        '''
        self.send_sock = socket(AF_INET, SOCK_STREAM)  # 创建TCP套接字
        self.send_sock.bind(self.tcp_address)
        print('绑定')
        self.send_sock.listen(5)
        while True:
            try:
                self.rec_sock, address = self.send_sock.accept()
                print('连接成功')
            except Exception:
                pass

    def send_message(self, message):
        '''
        该函数使用tcp发送控制信息
        :param message:
        :return:
        '''
        self.rec_sock.send(message.encode())

    def start(self):
        '''
        该函数用于启动线程，包括4个：发送线程、接收线程、视频显示线程和录像线程
        :return:
        '''
        send_thread = threading.Thread(target=self.init_tcp)
        rec_thread = threading.Thread(target=self.rec_frame)
        # rec_thread.daemon = True
        show_thread = threading.Thread(target=self.show_video)
        record_thread = threading.Thread(target=self.record_video)
        send_thread.start()
        rec_thread.start()
        show_thread.start()
        record_thread.start()

if __name__ == '__main__':
    udp_address = ('172.16.57.95', 8888)
    tcp_address = ('172.16.57.95', 7777)
    client = Client(udp_address, tcp_address)
    # client = Client(('192.168.43.246', 8888))
    client.start()
