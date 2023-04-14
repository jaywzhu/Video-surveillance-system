import socket
import struct
import time
import csv
import threading
from camera import Camera

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST # 服务器IP地址
        self.PORT = PORT  # 服务器端口号
        self.camera = Camera()

    def send(self, client_socket, addr):
        '''
        发送数据包
        :return:
        '''
        cap = self.camera.open_camera()
        while True:
            start_time = time.time()    # 计算时延
            frame = self.camera.get_frame(cap)
            middle_time = time.time()

            # 将数据打包发送
            client_socket.send(struct.pack("i", len(frame)))
            client_socket.send(frame)

            end_time = time.time()     # 计算时延
            img_delay = middle_time - start_time
            pack_delay = end_time - middle_time
            send_delay = end_time - start_time
            print(f'总发送时延：{send_delay:.3f}; 获取并编码图片时延：{img_delay:.3f}; 打包发送时延：{pack_delay:.3f}')
            delay = [round(send_delay, 3), round(img_delay, 3), round(pack_delay, 3)]
            with open('TCP_delay.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(delay)

    def start(self):
        '''
        多线程监听，等待客户端连接
        :return:
        '''
        # 建立TCP/IP连接
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.listen(5)

        # 接收客户端连接
        print('等待客户端连接...')
        while True:
            try:
                client_socket, addr = server_socket.accept()
            except Exception:
                break
            t = threading.Thread(target=self.send, args=(client_socket, addr))
            t.start()

        server_socket.close()

if __name__ == '__main__':
    # HOST = '172.16.57.95'  # 服务器IP地址
    HOST = '192.168.43.246'
    # HOST = '192.168.43.67'  # 服务器IP地址
    PORT = 5555  # 服务器端口号
    server = Server(HOST, PORT)
    server.start()
