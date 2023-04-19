import cv2

class Camera:

    def __init__(self):
        self.source = 0
        self.quality = 100
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]

    def open_camera(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 20)
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

    def get_quality(self):
        '''
        返回图像编码质量
        :param cap:
        :return:
        '''
        return self.quality

    def set_resolution(self, old_cap, order):
        '''
        根据需求提升或者降低分辨率
        :param old_cap:
        :param order:
        :return:
        '''
        resolution_list = [[320, 240], [640, 480], [1280, 720]]
        curr_res = self.get_resolution(old_cap)
        if order == 1:
            if curr_res[0] == 320:
                new_cap = cv2.VideoCapture(0)
                new_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                new_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return new_cap

            if curr_res[0] == 640:
                new_cap = cv2.VideoCapture(0)
                new_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                new_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                return new_cap

        if order == 0:
            if curr_res[0] == 1280:
                new_cap = cv2.VideoCapture(0)
                new_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                new_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return new_cap

            if curr_res[0] == 640:
                new_cap = cv2.VideoCapture(0)
                new_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                new_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                return new_cap

            if curr_res[0] == 320:
                print("Already the lowest resolution.")

    def set_quality(self, cap, order):
        resolution = self.get_resolution(cap)
        if order == 1:
            if resolution[0] >= 1280 and self.quality >= 70:
                return '该分辨率下已经达到最大值'
            if self.quality <= 80:
                self.quality += 5
                self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                return '图像质量已提高'
            else:
                return '图像质量以达到最大值'

        if order == 0:
            if self.quality > 0:
                self.quality -= 5
                self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                return '编码质量以降低'
            else:
                return '已经达到质量最小值'