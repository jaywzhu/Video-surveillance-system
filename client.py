import cv2
import socket
import struct
import numpy as np
import datetime

HOST = '192.168.43.67'  # 服务器IP地址
#HOST = '192.168.43.246'  # 服务器IP地址
PORT = 8888  # 服务器端口号

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('video.avi', fourcc, 25, (1280, 720))

# 建立TCP/IP连接
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

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

    # 截图功能
    key = cv2.waitKey(50)
    if key == ord('s'):  # 按下's'键，保存当前画面
        curr_time = datetime.datetime.now()
        time_str = datetime.datetime.strftime(curr_time, "%Y-%m-%d-%H-%M-%S")
        filename = f'snapshot_{time_str}'
        print(type(filename))
        print(filename)
        cv2.imwrite(f'E:/Py_Project/Test/screenshot/{filename}.jpg', frame)
        # cv2.imwrite(f'{filename}.jpg', frame)
        print(f'Snapshot saved to {filename}')

    elif key == 27:  # 按下'ESC'键，退出程序
        break

    #视频录制
    out.write(frame)

# 关闭连接
out.release()
client_socket.close()
cv2.destroyAllWindows()
