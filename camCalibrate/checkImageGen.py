import cv2
import time

# 選擇第二隻攝影機
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # set new dimensionns to cam object (not cap)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cnt = 0

while(True):
# 從攝影機擷取一張影像
    cnt+=1

    ret, frame = cap.read()

# 顯示圖片
    
    cv2.imshow('image', frame)

# 若按下 q 鍵則離開迴圈
    k = cv2.waitKey(1) & 0xFF
    if 27 == k:
        cv2.imwrite('test{}.jpg'.format(cnt) , frame)
        time.sleep(1)

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
