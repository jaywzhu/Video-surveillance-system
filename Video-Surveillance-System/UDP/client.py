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
        while True:
            data = None
            try:

                # 获取帧率
                fps, ret = s.recvfrom(4)
                fps = str(struct.unpack("i", fps)[0])
                print(f"帧率：{fps}")

                # 获取分辨率
                resolution, ret = s.recvfrom(8)
                width, height = struct.unpack("<ff", resolution)
                print(f"宽度，高度{width},{height}")

                # 解码视频
                start_time = time.time()   # 计算时间
                data, ret = s.recvfrom(921600)
                receive_data = np.frombuffer(data, dtype='uint8')
                r_img = cv2.imdecode(receive_data, 1)
                end_time = time.time()    # 计算时间

                # 显示时间
                font = cv2.FONT_HERSHEY_SIMPLEX
                current_time = str(datetime.datetime.now())
                r_img = cv2.putText(r_img, current_time, (0, 17), font, 0.6,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # 显示帧率
                r_img = cv2.putText(r_img, f'fps:{fps}', (int(width)-65, 17), font, 0.6,
                                    (0, 255, 255), 2, cv2.LINE_AA)

                # 视频显示
                try:
                    show_time = time.time()
                    cv2.imshow('server', r_img)
                    finish_time = time.time()
                except Exception as e:
                    pass
                rec_time = end_time - start_time
                show_time = finish_time - show_time
                rec_delay = finish_time - start_time
                print(f'总接收时延：{rec_delay:.3f};解包时延：{rec_time:.3f};显示时间：{show_time:.3f}')

                # 视频录制
                if set_flag == False:
                    self.out = cv2.VideoWriter('videoUDP.avi', self.fourcc, int(fps), (int(width), int(height)))
                    set_flag = True
                self.out.write(r_img)

            except BlockingIOError as e:
                pass

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def close_window(self):
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # client = Client(('172.16.57.95', 8888))
    client = Client(('192.168.43.246', 8888))

    client.show_video()