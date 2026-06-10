
from Utils import Utils

class PortDes(object):
    TAG = "PortDes"
    def __init__(self, portName, portId, nodeName,
                 nodeId, nodeInstance, nodeInstanceId):
        self.mPortName = portName
        self.mPortId = portId
        self.mNodeName = nodeName
        self.mNodeId = nodeId
        self.mNodeInstance = nodeInstance
        self.mNodeInstanceId = nodeInstanceId
        self.mPos = None
        self.mParentNodePos = None
        self.mOffest = 0
        self.mParent = None
        self.mPortNamePrune = None
        self.mWidth = 0
        self.mHeight = 0
        self.mTargetPort = False

    def __str__(self):
        return str("port_%s_%s_%s" % (self.mNodeId, self.mNodeInstanceId, self.mPortId))

    def setTargetPort(self, b):
        self.mTargetPort = b

    def isTargetPort(self):
        return self.mTargetPort

    def getPortName(self):
        return self.mPortName

    def getPortNamePrune(self):
        return self.mPortNamePrune

    def setPortNamePrune(self, name):
        self.mPortNamePrune = name

    def getPortId(self):
        return self.mPortId

    def getNodeName(self):
        return self.mNodeName

    def getNodeId(self):
        return self.mNodeId

    def getNodeInstance(self):
        return self.mNodeInstance

    def getNodeInstanceId(self):
        return self.mNodeInstanceId

    def setPortPos(self, pos):
        self.mPos = pos

    def getPortPos(self):
        return self.mPos

    def setParentNodePos(self, pos):
        self.mParentNodePos = pos

    def getParentNodePos(self):
        return self.mParentNodePos

    def setWidth(self, width):
        self.mWidth = width

    def getWidth(self):
        return self.mWidth

    def setHeight(self, height):
        self.mHeight = height

    def getHeight(self):
        return self.mHeight

    def match(self, port):
        result = False
        if self.mPortId == port.getPortId() and self.mNodeId == port.getNodeId() \
                and self.mNodeInstanceId == port.getNodeInstanceId() and self.mPortName.find(port.getPortName()) >= 0:
            result = True
        if self.mTargetPort or port.isTargetPort():
            if self.mPortName.find(port.getPortName()) < 0:
                result = False
        return result

    def print(self):
        Utils.LogD("      ", ("%s_%s" %
                            (str(self.mPortName),
                             str(self.mPortId))))