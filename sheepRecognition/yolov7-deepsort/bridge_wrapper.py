'''
A Moduele which binds Yolov7 repo with Deepsort with modifications
'''

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # comment out below line to enable tensorflow logging outputs
import time, datetime
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    
import cv2
import numpy as np
import matplotlib.pyplot as plt

# SQL imports
import sqlite3

from tensorflow.compat.v1 import ConfigProto # DeepSORT official implementation uses tf1.x so we have to do some modifications to avoid errors

# deep sort imports
from deep_sort import preprocessing, nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker

# import from helpers
from tracking_helpers import read_class_names, create_box_encoder
from detection_helpers import *

from pathlib import Path
from utils.general import custom_increment_path
from utils.sql_helper import sql_save

from utils.camRecieve.client import HttpCamera


# load configuration for object detector
config = ConfigProto()
config.gpu_options.allow_growth = True

class Goat_Tracking_Info:
    def __init__(self, log_time, track_id, img_id, start_frame, img):
        self.log_time = log_time
        self.id = track_id
        self.img_id = img_id
        self.duration = None
        self.start_frame = start_frame
        self.img = img

    def end_tracking_time(self):
        #self.duration = datetime.timedelta(milliseconds=(200*(frame_num - self.start_frame)))
        self.duration = datetime.datetime.now() - self.log_time

    def __hash__(self):
        return hash((self.id))
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.id == other.id



class YOLOv7_DeepSORT:
    '''
    Class to Wrap ANY detector  of YOLO type with DeepSORT
    '''
    def __init__(self, reID_model_path:str, detector, max_cosine_distance:float=0.7, nn_budget:float=None, nms_max_overlap:float=1.0,
    coco_names_path:str ="./io_data/input/classes/coco.names",  ):
        '''
        args: 
            reID_model_path: Path of the model which uses generates the embeddings for the cropped area for Re identification
            detector: object of YOLO models or any model which gives you detections as [x1,y1,x2,y2,scores, class]
            max_cosine_distance: Cosine Distance threshold for "SAME" person matching
            nn_budget:  If not None, fix samples per class to at most this number. Removes the oldest samples when the budget is reached.
            nms_max_overlap: Maximum NMs allowed for the tracker
            coco_file_path: File wich contains the path to coco naames
        '''
        self.detector = detector
        self.coco_names_path = coco_names_path
        self.nms_max_overlap = nms_max_overlap
        self.class_names = read_class_names()
        
        # initializing sql
        self.con = sqlite3.connect('goatTracking.db')
        self.cursorObj = self.con.cursor()


        # initialize deep sort
        self.encoder = create_box_encoder(reID_model_path, batch_size=1)
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget) # calculate cosine distance metric
        self.tracker = Tracker(metric) # initialize tracker

        #utilizing tracking info
        self.goat_tracking_set_curr = set()
        self.goat_tracking_set_prev = set()
        self.img_id = -1
        self.last_frame = []
        self.thresh = datetime.timedelta(seconds = 7)
        self.imageFolderPath = '/mnt/sda/goatData/images'
        self.videoResultPath = '/mnt/sda/goatData/videos'
        self.ended = False

        self.w = 0
        self.h = 0
        self.fps = 0
        self.out = None
        self.lastVideoSave = 0
        self.videoLength = 300

        


    def track_video(self,video:str='', output:bool=True, skip_frames:int=0, show_live:bool=False, count_objects:bool=False, verbose:int = 0):
        '''
        Track any given webcam or video
        args: 
            video: path to input video or set to 0 for webcam
            output: path to output video
            skip_frames: Skip every nth frame. After saving the video, it'll have very visuals experience due to skipped frames
            show_live: Whether to show live video tracking. Press the key 'q' to quit
            count_objects: count objects being tracked on screen
            verbose: print details on the screen allowed values 0,1,2
        
        try: # begin video capture
            vid = cv2.VideoCapture(int(video))
        except:
            vid = cv2.VideoCapture(video)
        '''
        cap = HttpCamera('http://sheeped01.ddns.net:6791/video_feed')
        cap.waitUntilReady()
        cap.read()
        assert cap.isOpened(), f'Failed to open HttpCam'

        if output: # get video ready to save locally if flag is set
            width = int(cap.getW())  # by default VideoCapture returns float instead of int
            height = int(cap.getH())
            fps = int(cap.getFPS())
            self.w = width
            self.h = height
            self.fps = fps
            self.lastVideoSave = datetime.datetime.now()
            codec_result = cv2.VideoWriter_fourcc(*"mp4v")
            codec_raw = cv2.VideoWriter_fourcc(*"mp4v")
            filename_result = self.lastVideoSave.strftime("result%Y%m%d-%H%M.mp4")
            filename_raw = self.lastVideoSave.strftime("raw%Y%m%d-%H%M.mp4")
            self.out_raw = cv2.VideoWriter(self.videoResultPath+f'/{filename_raw}', codec_raw, fps, (width, height))
            self.out_result = cv2.VideoWriter(self.videoResultPath+f'/{filename_result}', codec_result, fps, (width, height))

        frame_num = 0
        self.ended = False
        while True: # while video is running
            if verbose >= 1:start_time = time.time()

            return_value, frame = cap.read()
            if not return_value:
                print('Video has ended or failed!')
                frame = np.zeros((640,480,3)).astype(np.float32)
                self.ended = True
            frame_num +=1

            if skip_frames and not frame_num % skip_frames: continue # skip every nth frame. When every frame is not important, you can use this to fasten the process
            
            # -----------------------------------------PUT ANY DETECTION MODEL HERE -----------------------------------------------------------------
            seg_before_detect_time = time.time()

            yolo_dets = self.detector.detect(frame.copy(), plot_bb = False)  # Get the detections
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if yolo_dets is None:
                bboxes = []
                scores = []
                classes = []
                num_objects = 0
            
            else:
                bboxes = yolo_dets[:,:4]
                bboxes[:,2] = bboxes[:,2] - bboxes[:,0] # convert from xyxy to xywh
                bboxes[:,3] = bboxes[:,3] - bboxes[:,1]

                scores = yolo_dets[:,4]
                classes = yolo_dets[:,-1]
                num_objects = bboxes.shape[0]
            # ---------------------------------------- DETECTION PART COMPLETED ---------------------------------------------------------------------
            seg_before_track_time = time.time()

            names = []
            for i in range(num_objects): # loop through objects and use class index to get class name
                class_indx = int(classes[i])
                class_name = self.class_names[class_indx]
                names.append(class_name)

            names = np.array(names)
            count = len(names)

            if count_objects:
                cv2.putText(frame, "Objects being tracked: {}".format(count), (5, 35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (0, 0, 0), 2)

            # ---------------------------------- DeepSORT tacker work starts here ------------------------------------------------------------
            features = self.encoder(frame, bboxes) # encode detections and feed to tracker. [No of BB / detections per frame, embed_size]
            detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(bboxes, scores, names, features)] # [No of BB per frame] deep_sort.detection.Detection object

            cmap = plt.get_cmap('tab20b') #initialize color map
            colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

            boxs = np.array([d.tlwh for d in detections])  # run non-maxima supression below
            scores = np.array([d.confidence for d in detections])
            classes = np.array([d.class_name for d in detections])
            indices = preprocessing.non_max_suppression(boxs, classes, self.nms_max_overlap, scores)
            detections = [detections[i] for i in indices]       

            self.tracker.predict()  # Call the tracker
            self.tracker.update(detections) #  updtate using Kalman Gain

            seg_before_track_proc_time = time.time()

            self.goat_tracking_set_curr = set()
            curr_time = datetime.datetime.now()
            original_frame = frame.copy()
            for track in self.tracker.tracks:  # update new findings AKA tracks
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue 
                bbox = track.to_tlbr()
                #class_name = track.get_class()
                class_name = 'goat'
        
                #color = colors[int(track.track_id) % len(colors)]  # draw bbox on screen
                #color = [i * 255 for i in color]
                green = [199, 252, 0]
                red = [251, 111, 146]
                yellow = [241, 221, 2]
                color = green
                
                boundary = 250 
                points = np.array([[130, 40], [250, 40], [250, 480], [0, 480], [0, 170], [130, 170]], np.int32)
                cv2.polylines(frame, [points], True, yellow, 1)
                is_in_bound = False

                if bbox[0] < boundary:
                    if bbox[0] > 130:
                        if bbox[1] > 40:
                            color = red
                            is_in_bound = True
                    else:
                        if bbox[1] > 170:
                            color = red
                            is_in_bound = True
                        
                            
                
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 1)
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1]-20)), (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*13, int(bbox[1])), color, -1)
                cv2.putText(frame, class_name + " : " + str(track.track_id),(int(bbox[0]+2), int(bbox[1]-7)),0, 0.4, (20 ,20 , 20),1, lineType=cv2.LINE_AA)    

                curr_track_BBox_frame = original_frame.copy()
                cv2.rectangle(curr_track_BBox_frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 1)
                cv2.rectangle(curr_track_BBox_frame, (int(bbox[0]), int(bbox[1]-20)), (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*13, int(bbox[1])), color, -1)
                cv2.putText(curr_track_BBox_frame, class_name + " : " + str(track.track_id),(int(bbox[0]+2), int(bbox[1]-7)),0, 0.4, (20 ,20 , 20),1, lineType=cv2.LINE_AA)   
                
                if verbose == 2:
                    print("Tracker ID: {}, Class: {},  BBox Coords (xmin, ymin, xmax, ymax): {}".format(str(track.track_id), class_name, (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))))

                # ---------------------------------- Start goat logging -------------------------------------------------------------------------
                curr_img_id = -1
                curr_start_frame = frame_num

                if is_in_bound == False:
                    continue

                for goat in self.goat_tracking_set_prev:
                    if goat.img_id != -1 and goat.id == track.track_id:
                        curr_img_id = goat.img_id
                        curr_time = goat.log_time
                        curr_start_frame = goat.start_frame
                        curr_track_BBox_frame = goat.curr_track_BBox_frame
 
                goat_info = Goat_Tracking_Info(curr_time, track.track_id, curr_img_id, curr_start_frame, curr_track_BBox_frame)
                self.goat_tracking_set_curr.add(goat_info)

            seg_before_logging_time = time.time()

            new_goats = self.goat_tracking_set_curr - self.goat_tracking_set_prev
            missing_goats = self.goat_tracking_set_prev - self.goat_tracking_set_curr
            

            if new_goats != set():
                print(f"{len(new_goats)} new objects detected")

                for case in new_goats:
                    self.goat_tracking_set_prev.add(case)
                

            if missing_goats != set():

                saved = False   

                for case in missing_goats:
                    self.goat_tracking_set_prev.remove(case)
                    case.end_tracking_time()

                    if case.duration < self.thresh:
                        continue

                    if saved == False: 
                        if self.img_id is -1:
                            self.img_id = custom_increment_path(Path(self.imageFolderPath + '/image'), sep=' ') # increment run
                        else:
                            self.img_id += 1
                        saved = True
                        
                    case.img_id = self.img_id

                    save_dir = self.imageFolderPath + f"/image {self.img_id}"
                    save_path = str(save_dir) + ".jpg"
                    cv2.imwrite(save_path, case.img)
                    
                    sql_save(case.log_time, case.id, case.duration, case.img_id)
                    print(f"Data saved, track id: {case.id}, first shown img id: {case.img_id}")
                
            self.last_frame = frame

            # -------------------------------- Tracker work ENDS here -----------------------------------------------------------------------
            seg_before_output_time = time.time()

            if verbose >= 1:
                fps = 1.0 / (time.time() - start_time) # calculate frames per second of running detections
                if not count_objects: print(f"Processed frame no: {frame_num} || Current FPS: {round(fps,2)}")
                else: print(f"Processed frame no: {frame_num} || Current FPS: {round(fps,2)} || Objects tracked: {count}")

            #origin = np.asarray(original_frame)
            origin = cv2.cvtColor(original_frame, cv2.COLOR_RGB2BGR)

            #result = np.asarray(frame)
            result = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if self.ended == True:
                break
            
            if output: 
                self.out_result.write(result) # save output video
                self.out_raw.write(origin)

            if show_live:
                cv2.imshow("Output Video", result)
                if cv2.waitKey(1) & 0xFF == ord('q'): break


            if (curr_time - self.lastVideoSave).total_seconds() > self.videoLength:
                self.out_raw.release()
                self.out_result.release()
                self.lastVideoSave = curr_time
                codec_raw = cv2.VideoWriter_fourcc(*"mp4v")
                codec_result = cv2.VideoWriter_fourcc(*"mp4v")
                filename_raw = datetime.datetime.now().strftime("raw%Y%m%d-%H%M.mp4")
                filename_result = datetime.datetime.now().strftime("result%Y%m%d-%H%M.mp4")
                self.out_raw = cv2.VideoWriter(self.videoResultPath+f'/{filename_raw}', codec_raw, self.fps, (self.w, self.h))
                self.out_result = cv2.VideoWriter(self.videoResultPath+f'/{filename_result}', codec_result, self.fps, (self.w, self.h))

            seg_final_time = time.time()

            l1 = 100.0 * (start_time - seg_before_detect_time) / (start_time - seg_final_time)
            l2 = 100.0 * (seg_before_detect_time - seg_before_track_time) / (start_time - seg_final_time)
            l3 = 100.0 * (seg_before_track_time - seg_before_track_proc_time) / (start_time - seg_final_time)
            l4 = 100.0 * (seg_before_track_proc_time - seg_before_logging_time) / (start_time - seg_final_time)
            l5 = 100.0 * (seg_before_logging_time - seg_before_output_time) / (start_time - seg_final_time)
            l6 = 100.0 * (seg_before_output_time - seg_final_time) / (start_time - seg_final_time)

            print(f'Before detect time {l1:.1f}%')
            print(f'Detect time        {l2:.1f}%')
            print(f'Tracking time      {l3:.1f}%')
            print(f'Processing time    {l4:.1f}%')
            print(f'Goat logging time  {l5:.1f}%')
            print(f'Output time        {l6:.1f}%')
        
        cv2.destroyAllWindows()
