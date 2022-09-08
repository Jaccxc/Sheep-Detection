import time
import sys
from tracemalloc import start
import cv2

cam = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
fps = 20
rec_sec = 10
rec = cv2.VideoWriter('record//output02.mp4', fourcc, fps, (640,  480))
if not cam.isOpened():
    print("Le flux d'entrée ne peut être ouvert")
    sys.exit()
if not cam.isOpened():
    print("Le flux de sortie ne peut être ouvert")
    cam.release()
    sys.exit()
start_time = time.time_ns()
tps_img_sui = start_time + 1 / fps * 1e9
print('start recording')
while True:
    ret, img = cam.read()
    if not ret:
        print("erreur ou fin de la lecture du flux")
        break
    curr_time = time.time_ns()
    tps_gap = tps_img_sui - curr_time
    if tps_gap > 0:
        time.sleep(tps_gap * 1e-9)
    else:
        print("FPS trop grand")

    if curr_time-start_time > 1e9 * rec_sec:
        print('30 seconds recorded')
        break

    tps_img_sui += 1 / fps * 1e9
    rec.write(img)
    
cam.release()
rec.release()
cv2.destroyAllWindows()