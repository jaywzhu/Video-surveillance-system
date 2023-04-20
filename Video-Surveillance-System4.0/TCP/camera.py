import cv2

class Camera:

    def __init__(self):
        self.source = 0
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def open_camera(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not cap.isOpened():
            raise RuntimeError('摄像头打开错误.')
        return cap

    def get_frame(self, cap):
        '''
        获取视频帧
        :return:
        '''
        if not cap.isOpened():
            raise RuntimeError('摄像头打开错误.')

        # 返回一帧视频
        ret, frame = cap.read()
        return cv2.imencode('.jpg', frame, self.encode_param)[1].tobytes()