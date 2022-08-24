import cv2
import os
import sys
import time
import socket
import imagezmq

camera = cv2.VideoCapture(0)
rpi_name = socket.gethostname()
sender = imagezmq.ImageSender(connect_to='tcp://192.168.50.119:5555')

time.sleep(2.0)

while(True):
    ret, frame = camera.read()
    sender.send_image(rpi_name, frame)
    