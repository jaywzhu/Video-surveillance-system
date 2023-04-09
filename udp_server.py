import cv2
import numpy as np
import socket

capture = cv2.VideoCapture(0)

HOST = '192.168.43.246'  # 监听所有地址
PORT = 9000  # UDP端口号
dest_addr = ('192.168.43.246', 7777)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
# 设置发送缓冲区大小为2048个字节
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)


while True:
    ret, frame = capture.read()

    # 将帧转换为字节串
    data_bytes = np.array(cv2.imencode('.jpg', frame)[1]).tobytes()

    # 分割成每个包最大长度为1024字节的数据包，并打上序号
    packet_size = 1024
    packets = [data_bytes[i:i+packet_size] for i in range(0, len(data_bytes), packet_size)]
    packet_num = len(packets)

    # 发送数据包
    for i in range(packet_num):
        s.sendto(str(i).zfill(5).encode() + packets[i], dest_addr)
        print(len(str(i).zfill(5).encode() + packets[i]))
        # print(f'发送完毕{i}')


# Release everything if job is finished
capture.release()
cv2.destroyAllWindows()