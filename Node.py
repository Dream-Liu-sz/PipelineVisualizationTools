from Utils import Utils
from PyQt5.Qt import QPoint
from PyQt5.Qt import QSize
from PyQt5.Qt import QFontMetrics
from PyQt5.Qt import QFont
from PyQt5.Qt import QRect
import sys
from Port import PortDes


class NodeDes(object):
    TAG = "NodeDes"
    NodeAdditionalLengthMap = {"IFE": 52, "Stats": 22, "Auto": 22, "BPS": 30, "Sink": 4}
    SpecialNodeWidthMap = {"IFE": 6, "BPS": 6, "IPE": 6}
    disablePortNamePruneList = ["Sensor"]

    def __init__(self, name, id, instance, instanceId, targetName=""):
        self.mNodeNameArea = None
        self.mNodeName = name
        self.mNodeId = id
        self.mNodeInstance = instance
        self.mNodeInstanceId = instanceId
        self.mTargetName = targetName
        self.mIsSourceNode = False
        self.mOutputPortList = []
        self.mInputPortList = []
        self.mNodeLevelList = []
        self.mNodePropertyList = []
        self.mNodeLevelSet = set()
        self.mNodePos = None
        self.mPortPosMap = {}
        self.mNodeLevelKey = -1
        self.mMinWidth = 190
        self.mMinHeight = 82
        self.mNodeSize = QSize(self.mMinWidth, self.mMinHeight)
        self.mNodeNameTextWidth = 0
        self.mNodeNameTextHeight = 0
        # thisNode's output Port --> childNode's input Port
        self.mLinkDes = dict()
        # Stores child nodes that this node needs to output to, and which output ports lead to them
        # i.e., child node <---> this node's output port mapping
        self.mChildNodeToOutputPortMap = dict()
        # i.e., parent node <---> this node's input port mapping
        self.mParentNodeToInputPortMap = dict()
        self.mChildNodeSortList = []
        self.mParentNodeList = []
        self.mColor = None
        self.mFont = QFont()
        self.mFontSize = 24
        self.mTargetNode = False

    def setNodeProp(self, propName=None, propId=None, propDataType=None, propValue=None):
        prop = (propName, propId, propDataType, propValue)
        self.mNodePropertyList.append(prop)

    def getNodeProp(self):
        return self.mNodePropertyList

    def isTargetNode(self):
        return self.mTargetNode

    def getTargetName(self):
        return self.mTargetName

    def mergeTargetName(self, targetName):
        if targetName is None or len(str(targetName)) == 0:
            return
        targetName = str(targetName)
        if self.mTargetName is None or len(str(self.mTargetName)) == 0:
            self.mTargetName = targetName
        elif self.mTargetName.find(targetName) < 0:
            self.mTargetName = str(self.mTargetName) + "|" + targetName

    def setTargetNode(self, b):
        self.mTargetNode = b

    def getNodeName(self):
        return self.mNodeName

    def getNodeId(self):
        return self.mNodeId

    def getNodeInstance(self):
        return self.mNodeInstance

    def getNodeInstanceId(self):
        return self.mNodeInstanceId

    def isSourceNode(self):
        return self.mIsSourceNode

    def setSourceNodeFlag(self, flag):
        self.mIsSourceNode = flag

    def addOutputPort(self, port):
        self.mOutputPortList.append(port)

    def addInputPort(self, port):
        need = True
        if len(self.mInputPortList) > 0:
            for inputPort in self.mInputPortList:
                if inputPort.match(port):
                    need = False
        if need:
            self.mInputPortList.append(port)

    def matchPort(self, port):
        result = False
        if type(port) == PortDes:
            if self.mNodeId == port.getNodeId() and self.mNodeInstanceId == port.getNodeInstanceId():
                result = True

            if self.mTargetNode or port.isTargetPort():
                if self.mTargetName.find(port.getPortName()) < 0 and port.getPortName().find(self.mTargetName) < 0:
                    result = False

        return result

    def match(self, node):
        result = False
        if type(node) == NodeDes:
            if self.mNodeName == node.getNodeName() and self.mNodeId == node.getNodeId() and self.mNodeInstanceId == node.getNodeInstanceId():
                result = True
            elif self.mNodeId == node.getNodeId() and self.mNodeInstanceId == node.getNodeInstanceId():
                result = True
            if result and (self.mTargetNode or node.isTargetNode()):
                if self.mTargetName.find(node.getTargetName()) < 0 and node.getTargetName().find(self.mTargetName) < 0:
                    result = self.mNodeName == node.getNodeName()
        return result

    def updateLink(self, link):
        self.mLinkDes.update(link)

    def getLink(self):
        return self.mLinkDes

    def updateChildNodePortMap(self, node, port):
        # Build the map from this node's output Port to the child node it feeds
        # i.e., childNode <---> thisNode's outPutPort map
        if self.mChildNodeToOutputPortMap.get(node) == None:
            portList = [port]
            temp = {node: portList}
            self.mChildNodeToOutputPortMap.update(temp)
        else:
            portList = self.mChildNodeToOutputPortMap.get(node)
            portList.append(port)
            temp = {node: portList}
            self.mChildNodeToOutputPortMap.update(temp)

    def updateParentNodePortMap(self, node, port):
        # Build the map from this node's input Port to the parent node that feeds it
        # i.e., parentNode <---> thisNode's inputPort map
        if self.mParentNodeToInputPortMap.get(node) == None:
            list = [port]
            temp = {node: list}
            self.mParentNodeToInputPortMap.update(temp)
        else:
            list = self.mParentNodeToInputPortMap.get(node)
            list.append(port)
            temp = {node: list}
            self.mParentNodeToInputPortMap.update(temp)

    def setColor(self, color):
        self.mColor = color

    def getColor(self):
        return self.mColor

    def getChildNodePortMap(self):
        return self.mChildNodeToOutputPortMap

    def getParentNodePortMap(self):
        return self.mParentNodeToInputPortMap

    def setNodeFont(self, fontSize):
        self.mFontSize = fontSize
        self.mFont.setPixelSize(self.mFontSize)
        self.calNodeNameArea()

    def getNodeFontSize(self):
        return self.mFontSize

    def idPrunePortDisable(self, port):
        for nodeName in self.disablePortNamePruneList:
            if nodeName.find(port.getPortName()) > 0:
                return True

        return False

    def calNodeNameArea(self):
        # Calculate the area of the node name; later used to detect overlap with port name and node name
        self.mFont.setPixelSize(self.mFontSize)
        metrics = QFontMetrics(self.mFont)
        self.mNodeNameTextWidth = metrics.width(self.mNodeName)
        self.mNodeNameTextHeight = metrics.height()
        x = self.mNodeSize.width() / 2 - self.mNodeNameTextWidth / 2
        y = self.mNodeSize.height() / 2 + self.mNodeNameTextHeight / 2

        self.mNodeNameArea = QRect(x, y, self.mNodeNameTextWidth, self.mNodeNameTextHeight)

    def calOverlap(self, port, direction):
        Utils.LogV(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        portWidth = port.getWidth()
        portHeight = port.getHeight()
        portPos = port.getPortPos()
        if portPos is None:
            Utils.LogE(self.TAG, ("%s: %s pos is None" % (sys._getframe().f_code.co_name, port.getPortName())))

        xOffset = 0
        yOffset = 0
        '''
            1. If xOffset is negative, the input port overlaps the node name on the x axis.
            2. If xOffset is positive, the output port overlaps the node name on the x axis.
            3. When the output fully overlaps the node name.
        '''
        if direction:
            temp = self.mNodeNameArea.x() - (portPos.x() + portWidth)
            if temp < 0:
                xOffset = temp
        else:
            temp = self.mNodeNameArea.x() + self.mNodeNameArea.width() - portPos.x()
            if temp > 0:
                xOffset = temp
        '''
            1. Port overlaps the node name above: shift yOffset upward.
            2. Port overlaps the node name below: shift yOffset downward.
        '''
        if portPos.y() < self.mNodeNameArea.y():
            temp = (self.mNodeNameArea.y() - self.mNodeNameArea.height()) - portPos.y()
            if temp < 0:
                yOffset = temp
        else:
            temp = self.mNodeNameArea.y() - (portPos.y() - portHeight)
            if temp > 0:
                yOffset = temp

        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return xOffset, yOffset

    def isNeedPurne(self, portList, direction):
        # Determine whether pruning is needed.
        # direction: True for input ports, False for output ports
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        for port in portList:
            xOffset, yOffset = self.calOverlap(port, direction)
            if direction:
                if xOffset < 0:
                    return True
            else:
                if xOffset > 0:
                    return True
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return False

    def pruneInputPortName(self):
        # Prune port Name
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        mInputPortNeedPrune = self.isNeedPurne(self.mInputPortList, True)
        if mInputPortNeedPrune:
            for inputPort in self.mInputPortList:
                metrics = QFontMetrics(self.mFont)
                portName = inputPort.getPortName()
                idx = portName.find("Port")
                if idx < 0:
                    idx = 0
                pruneName = portName[idx:len(portName)]
                Utils.LogD(self.TAG, ("prune port name", pruneName))
                inputPort.setPortNamePrune(pruneName)
                inputPort.setWidth(metrics.width(pruneName))

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def pruneOutputPortName(self):
        # prune port Name
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        mOutputPortNeedPrune = self.isNeedPurne(self.mOutputPortList, False)
        if mOutputPortNeedPrune:
            for outputPort in self.mOutputPortList:
                if self.idPrunePortDisable(outputPort) == False:
                    metrics = QFontMetrics(self.mFont)
                    portName = outputPort.getPortName()
                    idx = portName.find("Port")
                    if idx < 0:
                        idx = 0
                    pruneName = portName[idx:len(portName)]
                    Utils.LogD(self.TAG, ("prune port name", pruneName))
                    outputPort.setPortNamePrune(pruneName)
                    outputPort.setWidth(metrics.width(pruneName))

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def calNodeSize(self):
        # Calculate node Size
        # width is calculated using SpecialNodeWidthMap
        # height step is also looked up in NodeAdditionalLengthMap
        length = 20
        for key in self.NodeAdditionalLengthMap.keys():
            if self.mNodeName.find(key) >= 0:
                length = self.NodeAdditionalLengthMap.get(key)

        widthStep = 0
        for key in self.SpecialNodeWidthMap.keys():
            if self.mNodeName.find(key) >= 0:
                widthStep = self.SpecialNodeWidthMap.get(key)

        if len(self.mInputPortList) > len(self.mOutputPortList):
            self.mNodeSize.setHeight(self.mMinHeight + len(self.mInputPortList) * length)
            self.mNodeSize.setWidth(self.mMinWidth + len(self.mInputPortList) * widthStep)
        else:
            self.mNodeSize.setHeight(self.mMinHeight + len(self.mOutputPortList) * length)
            self.mNodeSize.setWidth(self.mMinWidth + len(self.mOutputPortList) * widthStep)

    def sortOutputPort(self):
        Utils.LogV(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.mChildNodeSortList = list(self.mChildNodeToOutputPortMap.keys())

        if len(self.mChildNodeSortList) > 0:
            orgLength = len(self.mOutputPortList)
            self.mOutputPortList.clear()
            for node in self.mChildNodeSortList:
                portList = self.mChildNodeToOutputPortMap.get(node)
                for outputPort in portList:
                    need = True
                    for port in self.mOutputPortList:
                        if port.match(outputPort):
                            need = False
                    if need:
                        self.mOutputPortList.append(outputPort)

            newLength = len(self.mOutputPortList)
            if orgLength != newLength:
                Utils.LogE(self.TAG, ("%s: orgLength %d, newLength %d" % (sys._getframe().f_code.co_name, orgLength, newLength)))

        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def calPortPos(self):
        Utils.LogV(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        inputPortLength = len(self.mInputPortList)
        outputPortLength = len(self.mOutputPortList)
        inputPortPortion = int(self.mNodeSize.height() / (inputPortLength + 1)) if inputPortLength > 0 else 0
        for i, inputPort in enumerate(self.mInputPortList, start=1):
            pos = QPoint(0, inputPortPortion * i)
            inputPort.setPortPos(pos)
            inputPort.setParentNodePos(self.mNodePos)

        self.mFont.setPixelSize(self.mFontSize - 6)
        metrics = QFontMetrics(self.mFont)
        outputPortPortion = int(self.mNodeSize.height() / (outputPortLength + 1)) if outputPortLength > 0 else 0
        for i, outputPort in enumerate(self.mOutputPortList, start=1):
            portName = outputPort.getPortNamePrune() if outputPort.getPortNamePrune() is not None else outputPort.getPortName()
            textWidth = metrics.width(portName)
            pos = QPoint(self.mNodeSize.width() - textWidth, outputPortPortion * i)
            Utils.LogD(self.TAG, ("%s: name %s textWidth %d pos %s" % (outputPort, portName, textWidth, pos)))
            outputPort.setPortPos(pos)
            outputPort.setWidth(textWidth)
            outputPort.setParentNodePos(self.mNodePos)

        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def calOutputPortPosNew(self, font):
        '''
        # Calculate the outputPort position and the width/height of the portName
        '''
        metrics = QFontMetrics(font)
        outputPortLength = len(self.mOutputPortList)
        outputPortPortion = int(self.mNodeSize.height() / (outputPortLength + 1))
        i = 1
        for outputPort in self.mOutputPortList:
            textWidth = metrics.width(outputPort.getPortName())
            textHeight = metrics.height()
            pos = QPoint(self.mNodeSize.width() - textWidth, outputPortPortion * i)
            outputPort.setPortPos(pos)
            outputPort.setWidth(textWidth)
            outputPort.setHeight(textHeight)
            outputPort.setParentNodePos(self.mNodePos)
            i += 1

        self.calNodeNameArea()
        self.pruneOutputPortName()

    def calInputPortPos(self, font):
        inputPortLength = len(self.mInputPortList)
        inputPortPortion = int(self.mNodeSize.height() / (inputPortLength + 1))
        metrics = QFontMetrics(font)
        i = 1
        for inputPort in self.mInputPortList:
            textWidth = metrics.width(inputPort.getPortName())
            textHeight = metrics.height()
            pos = QPoint(0, inputPortPortion * i)
            inputPort.setPortPos(pos)
            inputPort.setParentNodePos(self.mNodePos)
            inputPort.setWidth(textWidth)
            inputPort.setHeight(textHeight)
            i += 1

        self.pruneInputPortName()

    def getChildNodeSortList(self):
        return self.mChildNodeSortList

    def setNodeLevel(self, level):
        self.mNodeLevelList.clear()
        self.mNodeLevelSet.add(level)
        for level in self.mNodeLevelSet:
            self.mNodeLevelList.append(level)
        # pipeline@2:
        # D : PipelineDes : calChildNodePosNew:currentLevelKey 9 parent FDManager0 level 9, child SinkNoBuffer4 level 9, getNext 16
        # Sort setNodeLevel from largest to smallest; otherwise parentNode and child would end up on the same level
        self.mNodeLevelList.sort(reverse=True)

    def sortLevelList(self):
        self.mNodeLevelList.sort(reverse=True)

    def getNodeLevel(self):
        return self.mNodeLevelList

    def getInputPort(self):
        return self.mInputPortList

    def getOutputPort(self):
        return self.mOutputPortList

    def setNodePos(self, pos):
        self.mNodePos = pos

    def getNodePos(self):
        return self.mNodePos

    def setNodeLevelKey(self, key):
        self.mNodeLevelKey = key

    def getNodeLevelKey(self):
        return self.mNodeLevelKey

    def setNodeSize(self, size):
        self.mNodeSize = size

    def getNodeSize(self):
        return self.mNodeSize

    def setPortPos(self, port, pos):
        port.setPortPos(pos)

    def getPortPos(self, port):
        return port.getPortPos()

    def getNodeOffest(self):
        return self.mTextWidth

    def print(self):
        msg = ""
        for level in self.mNodeLevelList:
            msg = msg + "L" + str(level) + "_"
        msg = msg[0:len(msg) - 1]

        Utils.LogD("    ", ("%s_%s_%s_%s_%s" %
                            (str(self.mNodeName),
                             str(self.mNodeId),
                             str(self.mNodeInstance),
                             str(self.mNodeInstanceId),
                             msg)))
        Utils.LogD("     ", "inputPort:")
        for inputPort in self.mInputPortList:
            inputPort.print()
        Utils.LogD("     ", "outputPort:")
        for outputPort in self.mOutputPortList:
            outputPort.print()
