from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
#Arguments
class Counter:
    def __init__(self):
        self.prototxt = "mobilenet_ssd/MobileNetSSD_deploy.prototxt"
        self.model = "mobilenet_ssd/MobileNetSSD_deploy.caffemodel"
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
        self.videoInput = "videos/example_01.mp4"
        self.skipFrames = 30
        self.confidence = 0.4
        self.coordinateList = list()

    def loadModel(self):
        # load our serialized model from disk
        print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe(self.prototxt,self.model)
        return net
    
    def loadVideo(self):
        # load our video from disk
        print("[INFO] opening video file")
        vs = cv2.VideoCapture(self.videoInput)
        return vs
    
    def loadWebcam(self):
        # load stream from webcam
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(2.0)
        return vs

    def draw_shape(self,event,x,y,flag,parm):
        if event == cv2.EVENT_LBUTTONDOWN:
            print('Cliked: ', (x,y))
            x2,y2 = x,y
            self.coordinateList.append(x2)
            self.coordinateList.append(y2)

    def coreCounter(self):
        #load model and video for process
        net = self.loadModel()
        vs = self.loadVideo()

        #writer will be used as video writer
        writer = None
        #W and H are frame dimensions
        W = None
        H = None
        #Centroid Tracker is created
        ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        trackers = []
        trackableObjects = {}
        x2,y2 = -1,-1
        coordinateList = list()
        #Total values for late informations
        totalFrames = 0
        totalDown = 0
        totalUp = 0

        #Start fps
        fps = FPS().start()
        
        #loop for video frames
        while True:
            frame = vs.read()
            #if it is videostream change the value
            frame = frame[1] #frame

            #if the video is over break the loop
            if self.videoInput is not None and frame is None:
                break
            
            frame = imutils.resize(frame,width=500)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if W is None or H is None:
                (H, W) = frame.shape[:2]

            status = "Waiting"
            rects = []

            if totalFrames % self.skipFrames == 0:
                status = "Detecting"
                trackers = []

                blob = cv2.dnn.blobFromImage(frame, 0.007843,(W, H), 127.5)
                net.setInput(blob)
                detections = net.forward()

                for i in np.arange(0, detections.shape[2]):
                    
                    confidence = detections[0, 0, i, 2]

                    if confidence > self.confidence:
                        
                        idx = int(detections[0, 0, i, 1])

                        if self.CLASSES[idx] != "person":
                            continue

                        box = detections[0, 0, i, 3:7] * np.array([W,H,W,H])
                        (startX, startY, endX, endY) = box.astype("int")

                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(startX, startY, endX, endY)
                        tracker.start_track(rgb, rect)

                        trackers.append(tracker)
            
            else:
                for tracker in trackers:
                    status = "Tracking"

                    tracker.update(rgb)
                    pos = tracker.get_position()

                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())

                    rects.append((startX, startY, endX, endY))

            cv2.line(frame, (0, H // 2), (W, H // 2), (0,255, 255), 2)

            objects = ct.update(rects)

            for(objectID, centroid) in objects.items():

                to = trackableObjects.get(objectID, None)

                if to is None:
                    to = TrackableObject(objectID, centroid)

                else:
                    y =[c[1] for c in  to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)

                    if not to.counted:

                        if direction < 0 and centroid[1] < H // 2:
                            totalUp += 1
                            to.counted = True

                        elif direction > 0 and centroid[1] > H // 2:
                            totalDown += 1
                            to.counted = True
                
                trackableObjects[objectID] = to

                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


            info = [
                ("Up", totalUp),
                ("Down", totalDown),
                ("Status", status),
            ]

            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i*20)+20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if writer is not None:
                writer.writer(frame)

            cv2.setMouseCallback('Frame',self.draw_shape)

            if (len(self.coordinateList) % 4 == 0 and len(self.coordinateList) != 0):
                temp = int(len(self.coordinateList) / 4)
                for i in range(temp):
                    cv2.line(frame, (self.coordinateList[i*4-4], self.coordinateList[i*4-3]), (self.coordinateList[i*4-2], self.coordinateList[i*4-1]), (255, 0, 0), 2)
                    cv2.imshow("Frame", frame)



            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            
            totalFrames += 1
            fps.update()

        fps.stop()

        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        #change if it uses webcam
        vs.release()  #vs.stop()
        cv2.destroyAllWindows()




    
