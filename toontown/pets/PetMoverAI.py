import random, math
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import *
from otp.movement.Mover import Mover 

estateRadius = 130
estateCenter = (0, -40)

houseRadius = 15
houses = ((60, 10), (42, 75), (-37, 35),  (80, -80), (-70, -120), (-55, -40))

dist = 2

def inCircle(x, y, c=estateCenter, r=estateRadius):
    center_x, center_y = c
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= r ** 2

def housePointCollision(x, y):
    for i, h in enumerate(houses):
        if inCircle(x, y, h, houseRadius):
            return 1

    return 0

def generatePos():
    def get():
        r = random.randint(0, estateRadius) - estateRadius / 2
        r2 = random.randint(0, estateRadius) - estateRadius / 2
        x = r + estateCenter[0]
        y = r2 + estateCenter[1]
        assert inCircle(x, y)
        return x, y

    p = get()
    while housePointCollision(*p):
        p = get()

    return p

def lineInCircle(pt1, pt2, circlePoint, circleRadius=houseRadius):
    x1, y1 = pt1
    x2, y2 = pt2

    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return 0

    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist

    t = dx * (circlePoint[0] - x1) + dy * (circlePoint[1] - y1)

    ex = t * dx + x1
    ey = t * dy + y1

    d2 = math.hypot(ex - circlePoint[0], ey - circlePoint[1])
    return d2 <= circleRadius

def houseCollision(pt1, pt2):
    for i, h in enumerate(houses):
        if lineInCircle(pt1, pt2, h):
            return 1

    return 0

def generatePath(start, end):
    points = [start]
    if not houseCollision(start, end):
        points.append(end)
        return points

    while True:
        next = generatePos()
        while houseCollision(points[-1], next):
            next = generatePos()

        points.append(next)
        if not houseCollision(next, end):
            points.append(end)
            return points

def angle(A, B):
    ax = A.getX()
    ay = A.getY()

    bx = B.getX()
    by = B.getY()

    return math.atan2(by-ay, bx-ax)

class PetMoverAI(FSM, Mover):
    notify = DirectNotifyGlobal.directNotify.newCategory("PetMoverAI")

    def __init__(self, pet):
        self.pet = pet
        self.fwdSpeed = 10.0
        self.rotSpeed = 360.0
        self.dt = 0
        FSM.__init__(self, 'PetMoverAI-%d' % self.pet.doId)
        Mover.__init__(self, self.pet, self.fwdSpeed, self.rotSpeed)
        self.chaseTarget = None
        self.__seq = None
        #self.__moveFromStill()
        self.__chaseCallback = None

    def enterStill(self):
        taskMgr.doMethodLater(random.randint(15, 60), self.__moveFromStill, self.pet.uniqueName('next-state'))

    def exitStill(self):
        taskMgr.remove(self.pet.uniqueName('next-state'))

    def __moveFromStill(self, task=None):
        choices = ["Wander"]
        nextState = random.choice(choices)
        self.request(nextState)

    def enterWander(self):
        target = self.getPoint()
        self.walkToPoint(target)

    def getPoint(self):
        x, y = generatePos()
        return Point3(x, y, 0)

    def walkToPoint(self, target):
        here = self.pet.getPos()
        dist = Vec3(here - target).length()

        self.__seq = Sequence(Func(self.pet.lookAt, target), Func(self.pet.setP, 0), self.pet.posInterval(dist / self.fwdSpeed, target, here),
                              Func(self.__stateComplete))
        self.__seq.start()

    def exitWander(self):
        if self.__seq:
            self.__seq.pause()

        self.__seq = None

    def __stateComplete(self):
        try:
            self.request("Still")
        except:
            pass
        
    def setDt(self, dt):
        self.dt = dt
        
    def getDt(self):
        return self.dt
        
    def addForce(self, force):
        self.notify.warning('addForce() -- Not Implemented Yet!')
        
    def addRotForce(self, rotForce):
        self.notify.warning('addRotForce() -- Not Implemented Yet!')
   
    def addShove(self, vel):
        self.notify.warning('addShove() -- Not Implemented Yet!')
        
    def addRotShove(self, rotVel):
        self.notify.warning('addRotShove() -- Not Implemented Yet!')
        '''newRot = rotVel - self.pet.getHpr()
        self.pet.setHpr(newRot)'''
    
    def destroy(self):
        self.demand("Off")

    def setFwdSpeed(self, speed):
        self.fwdSpeed = speed

    def getFwdSpeed(self):
        return self.fwdSpeed

    def setRotSpeed(self, speed):
        self.rotSpeed = speed

    def getRotSpeed(self):
        return self.rotSpeed
        
    def getNodePath(self):
        if self.pet and not self.pet.isEmpty():
            return self.pet
        return None
      
    def lock(self):
        if self.state != "Still":
            self.demand("Still")

    def enterChase(self, target=None):
        if not target:
            target = hidden.attachNewNode('target')
            target.setPos(self.getPoint())

        pos = target.getPos()
        theta = angle(self.pet.getPos(), pos) * (math.pi / 180)
        dx = dist * math.cos(theta)
        dy = dist * math.sin(theta)

        self.walkToPoint(Point3(pos.getX() - dx, pos.getY() - dy, pos.getZ()))

    def exitChase(self):
        if self.__chaseCallback:
            self.__chaseCallback()
            self.__chaseCallback = None

        if self.__seq:
            self.__seq.pause()

        self.__seq = None

    def walkToAvatar(self, av, callback=None):
        if callback:
            self.__chaseCallback = callback

        self.demand("Chase", av)
