from pyimagesearch.centroidtracker import CentroidTracker


class Camera_Information:

    def __init__(self, net, vs):
        self.net = net
        self.vs = vs
        self.writer = None
        self.W = None
        self.H = None
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackers = []
        self.trackableObjects = {}

        self.status = ""

        self.totalFrames = 0
        self.totalDown = 0
        self.totalUp = 0
        self.record = 0
        pass