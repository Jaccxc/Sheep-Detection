import numpy as np
import cv2
import glob

DIM=(1920, 1080)
K=np.array([[746.2375213865838, 0.0, 968.836703623176], [0.0, 744.0664602168284, 559.9185383737507], [0.0, 0.0, 1.0]])
D=np.array([[-0.03896429728025417], [-0.046694249674700025], [0.08308967520837052], [-0.04588079410525378]])

def undistort():
    images = glob.glob('image\*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        h,w = img.shape[:2]    
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
        undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)    
        cv2.imshow("distorted", img)
        cv2.imshow("undistorted", undistorted_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
if __name__ == '__main__':
    undistort()