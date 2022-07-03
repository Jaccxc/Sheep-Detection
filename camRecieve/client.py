import threading
import time

import cv2
import numpy as np
import requests

#from device.camera import Camera


class HttpCamera():
    def __init__(self, url):
        self.__url = url
        self.__frame = None
        self.__last_frame = None
        self.__running_flag = False  # 代表还在不在运行。

    def isOpened(self):
        return self.__running_flag

    def open(self):
        if self.isOpened():  # 如果已经open过了，第二次open就直接忽略。
            return
        response = requests.get(self.__url,
                                stream=True)  # 向目标url请求

        def tmp():
            bytes = b'\r\n'
            cst = b'\r\n--frame\r\nContent-Type: image/jpeg\r\n\r\n'
            now_position = 0  # 这一帧的开始位置
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    if not self.__running_flag:  # 如果在连接过程中用户close了，那就不用再执行了。
                        break
                    bytes += chunk
                    next_position = bytes.find(cst, now_position + 1)
                    if -1 != next_position:
                        bin_data = bytes[now_position + len(
                            cst):next_position]  # 截取出图片的二进制数据
                        self.__frame = cv2.imdecode(
                            np.frombuffer(bin_data, np.uint8),
                            cv2.IMREAD_UNCHANGED)
                        bytes = bytes[next_position:]
                        now_position = 0
                response.close()  # 释放连接。
            except Exception:
                self.__running_flag = False
                raise Exception('服务端结束了视频')

        self.__running_flag = True
        threading.Thread(target=tmp).start()
        return

    def read(self):
        if not self.isOpened():
            self.open()
        while True:
            if self.__frame is not None and id(self.__frame) != id(
                    self.__last_frame):
                self.__last_frame = self.__frame
                return True, self.__frame
            else:
                time.sleep(0.001)  # 让出CPU

    def release(self):
        self.__running_flag = False
        return


if '__main__' == __name__:
    camera = HttpCamera('http://127.0.0.1:5000/video_feed')
    while True:
        ret, image = camera.read()
        cv2.imshow('image', image)
        k = cv2.waitKey(1) & 0xFF
        if 27 == k:
            break
    cv2.destroyAllWindows()
    camera.release()