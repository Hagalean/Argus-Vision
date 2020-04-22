from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from line import Line
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
        self.lines =[]
        self.recordDuration = 15
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
            if not self.lines or self.lines[-1].complete:
                newLine = Line(len(self.lines),x,y,0)
                self.lines.append(newLine)
            else:
                self.lines[-1].addSecondCoordinates(x,y)
        if event == cv2.EVENT_RBUTTONDOWN:
            if not self.lines or self.lines[-1].complete:
                newLine = Line(len(self.lines),x,y,1)
                self.lines.append(newLine)
            else:
                self.lines[-1].addSecondCoordinates(x,y)
                
    
    def ccw(self,A,B,C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    def intersect(self,A,B,C,D):
        return self.ccw(A,C,D) != self.ccw(B,C,D) and self.ccw(A,B,C) != self.ccw(A,B,D)

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
        #Total values for late informations
        totalFrames = 0
        totalDown = 0
        totalUp = 0
        record = 0
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
                print(H,W)

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




            objects = ct.update(rects)

            for(objectID, centroid) in objects.items():

                to = trackableObjects.get(objectID, None)

                if to is None:
                    to = TrackableObject(objectID, centroid)

                else:
                    y =[c[1] for c in  to.centroids]
                    if len(to.centroids) > 1:
                        p1, p2 = to.centroids[-2:]
                        for i in self.lines:
                            if i.complete:
                                check = self.intersect([i.x1,i.y1],[i.x2,i.y2],p1,p2)
                                if check:
                                    if i.type == 0:
                                        print([i.x1,i.y1],[i.x2,i.y2],p1,p2, check)   
                                        i.itPassed()
                                    else:
                                        print("alert")
                                        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                                        start = time.time()
                                        outputPath = "output/"+str(start)+".mp4"
                                        writer = cv2.VideoWriter(outputPath, fourcc,30,(W, H), True)
                                        record = True
                                        

                    
                        
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
            

            cv2.setMouseCallback('Frame',self.draw_shape)
            for i in self.lines:
                if i.complete:
                    if i.type == 0:
                        cv2.line(frame, (i.x1, i.y1), (i.x2, i.y2), (255, 0, 0), 2)
                        cv2.imshow("Frame", frame)
                    elif i.type == 1:
                        cv2.line(frame, (i.x1, i.y1), (i.x2, i.y2), (255, 255, 0), 2)
                        cv2.imshow("Frame", frame)

                    

            if(record):
                writer.write(frame)
                end = time.time()
                if (end-start) > self.recordDuration:
                    writer.release()
                    record = False

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




    
