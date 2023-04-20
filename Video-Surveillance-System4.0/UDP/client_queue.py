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

                # 解码视频
                data, ret = s.recvfrom(65535)
                receive_data = np.frombuffer(data, dtype='uint8')
                r_img = cv2.imdecode(receive_data, 1)

                # 写入队列,该队列用于视频播放
                if self.img_queue.qsize() < 100:
                    frame_data = [camera_fps, resolution, r_img, quality]
                    self.img_queue.put(frame_data)
                else:
                    # 写拥塞控制
                    pass
                # 该队列用于存入录像文件
                if self.video_queue.qsize() < 100:
                    video_data = [camera_fps, resolution, r_img, quality]
                    self.video_queue.put(video_data)
                else:
                    pass

            except Exception as e:
                print(e)
                continue

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
        frame_count = 0
        start_time = time.time()
        while True:
            try:
                frame_data = self.get_frame_data()
                resolution = frame_data[1]
                width = int(resolution[0])
                height = int(resolution[1])
                frame = frame_data[2]
                quality = frame_data[3]

                # # 帧率计算
                # frame_count += 1
                # if frame_count >= 100:
                #     end_time = time.time()
                #     process_time = end_time - start_time
                #     fps = int(frame_count/process_time)
                #     start_time = end_time
                #     frame_count = 0

                # 帧率计算
                frame_count += 1
                end_time = time.time()
                if end_time-start_time > 2:
                    process_time = end_time-start_time
                    fps = int(frame_count/process_time)
                    start_time = end_time
                    frame_count = 0

                # 视频中使用的文本参数
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_color = (0, 255, 255)
                if width == 1280:
                    font_size = 1
                    font_thick = 2
                if width == 640:
                    font_size = 0.8
                    font_thick = 1
                if width == 320:
                    font_size = 0.5
                    font_thick = 1

                # 显示时间
                current_time = datetime.datetime.now()
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                time_text_size, _ = cv2.getTextSize(current_time, font, font_size, font_thick)
                time_text_location = (0, time_text_size[1])
                frame = cv2.putText(frame, current_time, time_text_location, font, font_size,
                                    font_color, font_thick, cv2.LINE_AA)

                # 显示帧率
                fps_text = f'fps:{fps}'
                fps_text_size, _ = cv2.getTextSize(fps_text, font, font_size, font_thick)
                fps_text_location = (width-fps_text_size[0], fps_text_size[1])
                frame = cv2.putText(frame, fps_text, fps_text_location, font, font_size,
                                    font_color, font_thick, cv2.LINE_AA)

                # 显示图像质量
                quality_text = quality
                quality_text_size, _ = cv2.getTextSize(quality_text, font, font_size, font_thick)
                quality_text_location = (width-quality_text_size[0], height-10)
                frame = cv2.putText(frame, quality_text, quality_text_location, font, font_size,
                                    font_color, font_thick, cv2.LINE_AA)

                # 显示分辨率
                resolution_text = f'{width}x{height}'
                resolution_text_size, _ = cv2.getTextSize(resolution_text, font, font_size, font_thick)
                resolution_text_location = (width - resolution_text_size[0],
                                            height - quality_text_size[1]-15)
                frame = cv2.putText(frame, resolution_text, resolution_text_location, font, font_size,
                                    font_color, font_thick, cv2.LINE_AA)

                # 显示视频
                cv2.namedWindow("client", cv2.WINDOW_AUTOSIZE)
                cv2.imshow('client', frame)

                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                # 按"r"和“t”键调节分辨率， “r”是提高分辨率，“t”是降低分辨率
                # "o"是提高图片 编码质量；“p”是降低图片编码质量
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

            except cv2.error:
                # 解包错误，丢掉这一帧
                continue
            except OSError:
                # 数据过大，丢掉这一帧
                continue
            except Exception as e:
                print(e)

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
            if video_end - video_start >= 120:  # 每隔一段时间录制一个视频
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
            except Exception as e:
                print(e)
                continue

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
    # udp_address = ('172.16.57.95', 8888)
    # tcp_address = ('172.16.57.95', 7777)
    udp_address = ('192.168.43.246', 8888)
    tcp_address = ('192.168.43.246', 7777)
    client = Client(udp_address, tcp_address)
    # client = Client(('192.168.43.246', 8888))
    client.start()
