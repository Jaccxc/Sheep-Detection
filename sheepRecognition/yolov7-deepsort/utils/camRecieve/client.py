import threading
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
import requests

#from device.camera import Camera


class HttpCamera():
    def __init__(self, url):
        self.__url = url
        self.__frame = np.array([])
        self.__last_frame = None
        self.__running_flag = False  # 代表还在不在运行。
        self.attemps = 3000 #斷線重連後最多需要嘗試幾次重新連線 每次間隔8秒
        self.h = -1
        self.w = -1
        self.c = -1
        self.fps = 5.0
        self.__first_frame_timestamp = None
        self.__last_frame_timestamp = datetime.now()
        self.__total_frame_count = 0

    def isOpened(self):
        return self.__running_flag

    def open(self):
        if self.isOpened():  # 如果已经open过了，第二次open就直接忽略。
            return
        for attemp in range(self.attemps):
            try:
                response = requests.get(self.__url,
                                        stream=True)  # 向目标url请求
                print('取得response')
                print(response)
            except Exception:
                print('目標影像來源沒有反應 重新連線中...')
                time.sleep(8)
            else:
                break
        else:
            raise Exception(f"重連超過嘗試次數上限: {self.attemps}次")

        def tmp():
            bytes = b'\r\n'
            cst = b'\r\n--frame\r\nContent-Type: image/jpeg\r\n\r\n'
            now_position = 0  # 这一帧的开始位置
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    if not self.__running_flag:  # 如果在连接过程中用户close了，那就不用再执行了。
                        raise Exception('主動結束連接')
                    bytes += chunk
                    next_position = bytes.find(cst, now_position + 1)
                    if -1 != next_position:
                        bin_data = bytes[now_position + len(
                            cst):next_position]  # 截取出图片的二进制数据
                        self.__frame = cv2.imdecode(
                            np.frombuffer(bin_data, np.uint8),
                            cv2.IMREAD_UNCHANGED)
                        self.h, self.w, self.c = self.__frame.shape
                        #print(f'img height = {self.h}, width = {self.w}')
                        bytes = bytes[next_position:]
                        now_position = 0
                response.close()  # 释放连接。
            except Exception:
                self.__running_flag = False
                print('影像端停止輸入 嘗試重新建立連線')
                time.sleep(8)
                return
                #raise Exception('影像端停止輸入')

        self.__running_flag = True
        threading.Thread(target=tmp).start()
        time.sleep(1)
        return

    def waitUntilReady(self):
        if not self.isOpened():
            self.open()
        while True:
            if self.__frame.size != 0:
                break;
            else:
                print('Waiting for first image...')
                time.sleep(8)

    def read(self):
        #print(f'current state {self.__running_flag}')
        if not self.isOpened():
            self.open()
        #print('still reading')
        now = datetime.now()
        while now - self.__last_frame_timestamp < timedelta(seconds=1.0/self.fps):
            time.sleep(0.001)  # 让出CPU
            now = datetime.now()
        if id(self.__last_frame) != id(self.__frame):
            elapsed = '---'
            avg = '---'
            fps = '---'
            self.__total_frame_count += 1

            if self.__first_frame_timestamp == None:
                self.__first_frame_timestamp = now
            
            self.__last_frame_timestamp = now
            '''
            else:
                elapsed = str(now - self.__last_frame_timestamp)[0:11]
                avg = f'{((now - self.__first_frame_timestamp).total_seconds() / (self.__total_frame_count-1)) : .3f}'
                fps = f'{(1.0 / eval(avg)) : .3f}'

                self.__last_frame_timestamp = now
            '''

            #print(f'image saved, timestamp: {now.strftime("%m%d_%H-%M-%S")}, elapsed: {elapsed}, avg frame: {avg}, fps: {fps}')
            #cv2.imwrite('C:\\Users\\User\\Desktop\\sheep_image\\' + now.strftime("%m%d_%H-%M-%S") + '.png', self.__frame)

        time_after_last_frame = now - self.__last_frame_timestamp

        if time_after_last_frame > timedelta(seconds = 120):
            print(f'現在時間{now.strftime("%m%d_%H-%M-%S")} 自從上次接收到新畫面已過2分鐘 嘗試重新連線中')
            self.__last_frame_timestamp = now
            self.__running_flag = False


        self.__last_frame = self.__frame
        return True, self.__frame
        


    def release(self):
        self.__running_flag = False
        return

    def getW(self):
        if self.w == -1:
            raise Exception('鏡頭尚未初始化')
        return self.w
    
    def getH(self):
        if self.h == -1:
            raise Exception('鏡頭尚未初始化')
        return self.h

    def getFPS(self):
        return int(self.fps)


if '__main__' == __name__:
    camera = HttpCamera('http://sheeped01.ddns.net:6796/video_feed')
    camera.waitUntilReady()
    while True:
        ret, image = camera.read()
        if not ret:
            image = cv2.imread('no_sig.png')
        cv2.imshow('image', image)
        k = cv2.waitKey(1) & 0xFF
        if 27 == k:
            break
    cv2.destroyAllWindows()
    camera.release()
