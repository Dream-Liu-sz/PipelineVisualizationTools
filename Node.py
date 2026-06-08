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
        # 存放此node需要输出的那些child node，以及是此node的哪些output port 输出到 这些child node
        # 即childNode <---> thisNode's outPutPort的map
        self.mChildNodeToOutputPortMap = dict()
        # 即ParentNode <---> thisNode's inputPort的map
        self.mParentNodeToInputPortMap = dict()
        self.mChildNodeSortList = []
        self.mParentNodeList = []
        self.mColor = None
        self.mFont = QFont()
        self.mFontSize = 24
        self.mTargetNode = False

    def setNodePorp(self, propName=None, propId=None, propDataType=None, propValue=None):
        prop = (propName, propId, propDataType, propValue)
        self.mNodePropertyList.append(prop)

    def getNodeProp(self):
        return self.mNodePropertyList

    def isTargetNode(self):
        return self.mTargetNode

    def getTargetName(self):
        return self.mTargetName

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
                if self.mTargetName.find(port.getPortName()) < 0:
                    result = False

        return result

    def match(self, node):
        result = False
        if type(node) == NodeDes:
            if self.mNodeId == node.getNodeId() and self.mNodeInstanceId == node.getNodeInstanceId():
                result = True
            if self.mTargetNode or node.isTargetNode():
                if self.mTargetName.find(node.getTargetName()) < 0:
                    result = False
                # Utils.LogI("    ", ("this %s_%s_%s_%s --> input %s_%s_%s" %
                #                     (str(self.mNodeName),
                #                      str(self.mNodeId),
                #                      str(self.mNodeInstance),
                #                      str(self.mNodeInstanceId),
                #                      node.getNodeName(), node.getNodeId(), node.getNodeInstanceId())))
        return result

    def updateLink(self, link):
        self.mLinkDes.update(link)

    def getLink(self):
        return self.mLinkDes

    def updateChildNodePortMap(self, node, port):
        '''
        @Func:create此node的Output Port对应输出的node的map
            即 childNode <---> thisNode's outPutPort 的 map
        '''
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
        '''
        @Func:create此node的Input Port对应输入的node的map
            即 ParentNode <---> thisNode's inputPort 的 map
        '''
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
        '''
        @Func:计算 node name 的 ared，后面会用来计算port name 和 node Name是否有重合
        '''
        # Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.mFont.setPixelSize(self.mFontSize)
        metrics = QFontMetrics(self.mFont)
        self.mNodeNameTextWidth = metrics.width(self.mNodeName)
        self.mNodeNameTextHeight = metrics.height()
        x = self.mNodeSize.width() / 2 - self.mNodeNameTextWidth / 2
        y = self.mNodeSize.height() / 2 + self.mNodeNameTextHeight / 2

        self.mNodeNameArea = QRect(x, y, self.mNodeNameTextWidth, self.mNodeNameTextHeight)
        # Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

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
            1. xoffset如果小于0，则为inputPort x方向有重叠
            2. xoffset如果大于0，则为outputPort x方向有重叠
            3. output 全覆盖时
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
            1. port 在上方与node name有覆盖，上移yOffset 
            2. port 在下方与node name有覆盖，下移yOffset
        '''
        if portPos.y() < self.mNodeNameArea.y():
            # temp = self.mNodeNameArea.y() - (portPos.y() + portHeight)
            temp = (self.mNodeNameArea.y() - self.mNodeNameArea.height()) - portPos.y()
            if temp < 0:
                # yOffset = self.mNodeNameArea.height() + self.mNodeNameArea.y() - portPos.y()
                yOffset = temp
        else:
            temp = self.mNodeNameArea.y() - (portPos.y() - portHeight)
            if temp > 0:
                yOffset = temp

        # Utils.LogD(self.TAG, ("%s: - %s offset x %d y %d, portXY %d %d, width %d height %d, selfArea.XY %d %d, width %d height %d" % (
        #     sys._getframe().f_code.co_name, port.getPortName(), xOffset, yOffset, portPos.x(), portPos.y(), portWidth, portHeight,
        #     self.mNodeNameArea.x(), self.mNodeNameArea.y(), self.mNodeNameArea.width(), self.mNodeNameArea.height())))
        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return xOffset, yOffset

    def isNeedPurne(self, portList, direction):
        '''
            @Func:计算是否需要 Purne
            @direction: True 为input，False 为Output
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        for port in portList:
            xOffset, yOffset = self.calOverlap(port, direction)
            if direction:
                if xOffset < 0:
                    return True
            else:
                if xOffset > 0:
                    # Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
                    return True
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return False

    def pruneInputPortName(self):
        '''
        @Func:prune port Name
        '''
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
        '''
        @Func:prune port Name
        '''
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
        '''
        @Func:计算node的Size
            width 根据 SpecialNodeWidthMap 中的来计算
            height 的 step也需要从NodeAdditionalLengthMap查找
        '''
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
        # 计算outputPort的pos，以及portName的width height
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
        '''
            pipeline@2:
            D : PipelineDes : calChildNodePosNew:currentLevelKey 9 parent FDManager0 level 9, child SinkNoBuffer4 level 9, getNext 16
            setNodeLevel时从大到小排序，不然会导致 parentNode 与 child 同级
        '''
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
