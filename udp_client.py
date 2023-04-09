import cv2
import numpy as np
import socket

HOST = '192.168.43.246'  # 监听所有地址
PORT = 7777  # UDP端口号

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
# 设置接收缓冲区大小为2048个字节
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048)
print('Waiting for data...')

while True:
    # 接收包的序号和数据
    print("开始")
    recv_data, addr = s.recvfrom(1029)
    print("接收了")
    packet_num_str = recv_data[:5].decode()
    packet_data = recv_data[5:]
    print(packet_num_str)
    print(packet_data)

    if packet_num_str == 'endss':
        break
    image_bytes = b''
    # 将字节串转换为帧图像
    if packet_num_str == 'start':
        image_bytes = bytearray(packet_data)
    else:
        image_bytes += bytearray(packet_data)

    if len(packet_data) < 1029:
        # 已经接收到最后一个数据包，重组图像并显示
        frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), -1)
        cv2.imshow('Video', frame)
        cv2.waitKey(50)

# Release everything if job is finished
cv2.destroyAllWindows()