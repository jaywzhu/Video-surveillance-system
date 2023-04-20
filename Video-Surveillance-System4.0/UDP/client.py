import numpy as np
import cv2
import datetime
import time
import struct
from socket import *

class Client:
    def __init__(self, addr):
        self.addr = addr
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('videoUDP.avi', self.fourcc, 30, (1280, 720))

    def show_video(self):
        '''
        绑定地址，接收数据包，并解码展示视频
        :return:
        '''
        s = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        s.bind(self.addr)
        # s.setblocking(0)  # 设置为非阻塞模式

        set_flag = False    # 用于标记视频录制的参数是否已经设置， 只设置一次
        count_time = time.time()    # 帧率显示的时间间隔
        video_start = time.time()    # 视频文件每一分钟录制一个
        fps = ''
        while True:
            data = None
            try:
                # 获取帧率
                camera_fps, ret = s.recvfrom(4)
                camera_fps = str(struct.unpack("i", camera_fps)[0])
                print(f"帧率：{fps}")

                # 获取分辨率
                resolution, ret = s.recvfrom(8)
                width, height = struct.unpack("<ff", resolution)
                print(f"宽度，高度{width},{height}")

                # 解码视频
                start_time = time.time()   # 计算时间
                data, ret = s.recvfrom(65535)
                receive_data = np.frombuffer(data, dtype='uint8')
                r_img = cv2.imdecode(receive_data, 1)
                end_time = time.time()    # 计算时间

                # 接收端帧率
                now = time.time()
                if now-count_time >= 1:
                    frame_time = end_time - start_time
                    if not frame_time == 0:
                        fps = str(int(1.0/frame_time))
                    count_time = now

                # 显示时间
                font = cv2.FONT_HERSHEY_SIMPLEX
                current_time = datetime.datetime.now()
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                r_img = cv2.putText(r_img, current_time, (0, 17), font, 0.6,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # 显示帧率
                r_img = cv2.putText(r_img, f'fps:{fps}', (int(width)-85, 17), font, 0.6,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # 视频显示
                show_time = time.time()
                cv2.imshow('server', r_img)
                finish_time = time.time()

                rec_time = end_time - start_time
                show_time = finish_time - show_time
                rec_delay = finish_time - start_time
                print(f'总接收时延：{rec_delay:.3f};解包时延：{rec_time:.3f};显示时间：{show_time:.3f}')

                # 视频录制
                now = datetime.datetime.now()
                formatted_time = now.strftime('%Y_%m_%d_%H-%M-%S')
                if set_flag == False:
                    self.out = cv2.VideoWriter(f'video_file/{formatted_time}.avi',
                                               self.fourcc, int(camera_fps), (int(width), int(height)))
                    set_flag = True
                self.out.write(r_img)
                video_end = time.time()
                if video_end - video_start >= 10:    # 每隔十秒录制一个视频
                    set_flag = False
                    video_start = video_end

            except BlockingIOError as e:
                pass
            # except OSError as e:
            #     pass
            # except Exception as e:
            #     pass

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def close_window(self):
        cv2.destroyAllWindows()

if __name__ == '__main__':
    client = Client(('172.16.57.95', 8888))
    # client = Client(('192.168.43.246', 8888))
    client.show_video()