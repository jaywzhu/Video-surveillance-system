import cv2
import socket
import struct
import numpy as np
import datetime

class Client:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('video.avi', self.fourcc, 15, (1280, 720))

    def show_video(self):
        '''
        连接服务器，解码视频并播放
        :return:
        '''
        print("开始尝试建立连接")
        # 建立TCP/IP连接
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.HOST, self.PORT))
        print("连接成功")

        # 接收服务器发送的视频数据并播放
        while True:
            # 接收数据长度
            data_len = client_socket.recv(4)
            if not data_len:
                break
            # 解析数据长度
            data_len = struct.unpack("i", data_len)[0]
            # 接收数据
            data = b""
            while len(data) < data_len:
                packet = client_socket.recv(data_len - len(data))
                if not packet:
                    break
                data += packet
            # 解码视频数据并播放
            imgdata = np.frombuffer(data, dtype='uint8')
            frame = cv2.imdecode(imgdata, 1)
            cv2.imshow('video', frame)
            cv2.waitKey(20)

            # 视频录制
            self.out.write(frame)

            # 截图功能, 按下“s”保存当前画面
            key = cv2.waitKey(50)
            if key == ord('s'):  # 按下's'键，保存当前画面
                curr_time = datetime.datetime.now()
                time_str = datetime.datetime.strftime(curr_time, "%Y-%m-%d-%H-%M-%S")
                filename = f'snapshot_{time_str}'
                print(filename)
                cv2.imwrite(f'E:/Py_Project/Test/screenshot/{filename}.jpg', frame)
                # cv2.imwrite(f'{filename}.jpg', frame)
                print(f'Snapshot saved to {filename}')

            elif key == 27:  # 按下'ESC'键，退出程序
                self.close_connection()


    def close_connection(self):
        '''
        关闭socket连接，释放所有窗口
        :return:
        '''
        self.out.release()
        self.client_socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    HOST = '172.16.57.95'  # 服务器IP地址
    # HOST = '192.168.43.246'
    # HOST = '192.168.43.67'  # 服务器IP地址
    PORT = 5555  # 服务器端口号
    client = Client(HOST, PORT)
    client.show_video()