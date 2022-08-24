from detection_helpers import *
from tracking_helpers import *
from bridge_wrapper import *
from PIL import Image

import os
os.environ["KMP_DUPLICATE_LIB_OK"]  =  "TRUE"

detector = Detector(classes = [0]) # it'll detect ONLY [person,horses,sports ball]. class = None means detect all classes. List info at: "data/coco.yaml"
detector.load_model('yolov7.pt',) # pass the path to the trained weight file

tracker = YOLOv7_DeepSORT(reID_model_path="./deep_sort/model_weights/mars-small128.pb", detector=detector)
tracker.track_video(1 , output="./IO_data/output/street.avi", show_live = True, skip_frames = 0, count_objects = True, verbose=1)

