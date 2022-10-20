from detection_helpers import *
from tracking_helpers import *
from bridge_wrapper import *
from PIL import Image

import torch
print(torch.cuda.device_count())

import os
os.environ["KMP_DUPLICATE_LIB_OK"]  =  "TRUE"

detector = Detector(classes = None) # it'll detect ONLY [person,horses,sports ball]. class = None means detect all classes. List info at: "data/coco.yaml"
detector.load_model('best.pt',) # pass the path to the trained weight file

tracker = YOLOv7_DeepSORT(reID_model_path="./deep_sort/model_weights/mars-small128.pb", detector=detector)
video_title = 'conc220928-15-20-3d'
for _ in range(1):
    tracker.track_video(f"./IO_data/input/video/{video_title}.mp4" , output=f"./IO_data/output/done{video_title}.mp4", show_live = False, skip_frames = 0, count_objects = True, verbose=1)
#tracker.track_video(1 , output="./IO_data/output/O1_result.avi", show_live = True, skip_frames = 0, count_objects = True, verbose=1)
