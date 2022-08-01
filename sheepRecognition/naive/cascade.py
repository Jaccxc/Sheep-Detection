#!/usr/bin/python                                  
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# camera_face_detect.py
# Face detect from camera
#
# Date   : 06/22/2014
# Usage  : python camera_face_detect.py haarcascade_frontalface_default.xml

import threading
import time

import numpy as np
import requests

import sys
import cv2

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


#CAM_WIDTH, CAM_HEIGHT = 640, 480  #cali not working
#CAM_WIDTH, CAM_HEIGHT = 1280, 720  #cali not working
CAM_WIDTH, CAM_HEIGHT = 1920, 1080
DEBUG_CAM=0
CASCADE=0

        
DIM=(CAM_WIDTH, CAM_HEIGHT)
'''
K=np.array([[746.2375213865838, 0.0, 968.836703623176], [0.0, 744.0664602168284, 559.9185383737507], [0.0, 0.0, 1.0]])
D=np.array([[-0.03896429728025417], [-0.046694249674700025], [0.08308967520837052], [-0.04588079410525378]])
'''
K=np.array([[735.6199468787531, 0.0, 949.6281129943385], [0.0, 733.3174407954972, 511.0838841303066], [0.0, 0.0, 1.0]])
D=np.array([[-0.033712631321841935], [-0.005952529309371836], [-0.0037130841838726044], [0.001387399889887952]])

def undistort(img):
    h,w = img.shape[:2]    
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)    
    return undistorted_img



#cap = HttpCamera('http://127.0.0.1:5000/video_feed')
if(DEBUG_CAM):
    cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)  # set new dimensionns to cam object (not cap)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
else:
    cap = HttpCamera('http://192.168.0.28:5000/video_feed')

if(CASCADE):
    faceCascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')



while True:
    # Capture frame-by-frame
    before = time.time()
    ret, frame = cap.read()

    cv2.imshow('image', frame)
    frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA)
    frame = undistort(frame)

    if(CASCADE):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )


        after = time.time()
        print ("Found {0} faces!, fps= {1}".format(len(faces), round(1/(after-before), 1)))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


    # Display the resulting frame
    cv2.imshow("preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()