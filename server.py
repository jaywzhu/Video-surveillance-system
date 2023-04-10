import socket
import struct
import threading
from camera import Camera

class Server:
    def __init__(self):
        self.HOST = '192.168.43.246'  # 服务器IP地址
        self.PORT = 5555  # 服务器端口号
        self.camera = Camera()

    def send(self, client_socket, addr):
        '''
        发送数据包
        :return:
        '''
        cap = self.camera.open_camera()
        while True:
            frame = self.camera.get_frame(cap)
            # 将数据打包发送
            client_socket.send(struct.pack("i", len(frame)))
            client_socket.send(frame)

    def start(self):
        '''
        多线程监听，等待客户端接收
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
    server =Server()
    server.start()
