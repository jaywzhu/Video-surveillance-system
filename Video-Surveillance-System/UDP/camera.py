import cv2

class Camera:

    def __init__(self):
        self.source = 0
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

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

    def get_fps(self, cap):
        '''
        获取视频帧率
        :param cap:
        :return:
        '''
        return cap.get(5)

    def get_resolution(self, cap):
        '''
        获取当前视频分辨率
        :param cap:
        :return:
        '''
        return [cap.get(3), cap.get(4)]

    def set_resolution(self, cap, order):
        '''
        根据需求提升或者降低分辨率
        :param cap:
        :param order:
        :return:
        '''
        resolution_list = [[320, 240], [640, 480], [1280, 720], [1920, 1080]]
        curr_res = self.get_resolution(cap)

        if order == 1:
            if curr_res[0] == 320:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if curr_res[0] == 640:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if curr_res[0] == 1280:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            if curr_res[0] == 1920:
                print("Already the highest resolution.")

        if order == 0:
            if curr_res[0] == 1920:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if curr_res[0] == 1280:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if curr_res[0] == 640:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

            if curr_res[0] == 320:
                print("Already the lowest resolution.")
