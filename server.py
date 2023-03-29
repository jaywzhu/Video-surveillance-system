import cv2
import socket
import struct
import numpy as np
import threading

HOST = '192.168.43.67'  # 服务器IP地址
PORT = 8888  # 服务器端口号


def video_capture(client_socket, addr):
    print('客户端已连接：', addr)
    # 采集视频数据并传输给客户端
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        ret, frame = cap.read()
        # 编码视频数据
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        string_data = data.tobytes()
        # 将数据打包发送
        client_socket.send(struct.pack("i", len(string_data)))
        client_socket.send(string_data)

    # 关闭连接
    cap.release()
    client_socket.close()

# 建立TCP/IP连接
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# 接收客户端连接
print('等待客户端连接...')
while True:
    try:
        client_socket, addr = server_socket.accept()
    except Exception:
        break
    t = threading.Thread(target=video_capture, args=(client_socket, addr))
    t.start()

server_socket.close()
