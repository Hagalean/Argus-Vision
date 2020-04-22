class Line:
    def __init__(self,id,x1,y1,type):
        self.x1 = x1
        self.y1 = y1
        self.x2 = None
        self.y2 = None
        self.complete = False
        self.id = id
        self.passed = 0
        self.type = type
    
    def addSecondCoordinates(self,x2,y2):
        self.x2 = x2
        self.y2 = y2
        self.complete = True
    
    def itPassed(self):
        self.passed += 1
