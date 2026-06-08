from Utils import Utils
from PyQt5.Qt import QPoint
from PyQt5.Qt import QFont
from PyQt5.Qt import QRect
from PyQt5.Qt import QMessageBox
import sys


class PipelineDes(object):
    TAG = "PipelineDes"

    def __init__(self):
        self.mNodeList = []
        self.mNodeSrcPortDes = {}
        self.mNodeDstPortDes = {}
        self.mPortLinkDes = {}
        self.mSrcNodeNameList = []
        self.mSrcNodeList = []
        self.mPipelineName = ""
        self.mNodeGraph = {}
        self.mMaxLevel = 0
        self.mNodeLevelKeyMap = dict()
        self.mNodeLevelKeyList = []
        self.mLevelNodePosMap = dict()
        self.mInputPortList = []
        self.mBuild = False
        self.mParentWidget = None

    def updateNodeToSrcPortMap(self, nodeId, port):
        portList = self.mNodeSrcPortDes.get(nodeId)
        if portList is not None:
            portList.append(port)
            temp = {nodeId: portList}
            self.mNodeSrcPortDes.update(temp)
        else:
            portList = [port]
            temp = {nodeId: portList}
            self.mNodeSrcPortDes.update(temp)

    def updateNodeToDstPortMap(self, nodeId, port):
        portList = self.mNodeDstPortDes.get(nodeId)
        if portList is not None:
            portList.append(port)
            temp = {nodeId: portList}
            self.mNodeDstPortDes.update(temp)
        else:
            portList = [port]
            temp = {nodeId: portList}
            self.mNodeDstPortDes.update(temp)

    def updatePortToProtMap(self, srcPort, dstPortList):
        isExist = False
        temp = None
        for outputPort in self.mPortLinkDes.keys():
            if outputPort.match(srcPort):
                srcPort = outputPort
                isExist = True

        if isExist:
            portList = self.mPortLinkDes.get(srcPort)
            for port in dstPortList:
                portList.append(port)
            temp = {srcPort: portList}
        else:
            temp = {srcPort: dstPortList}

        self.mPortLinkDes.update(temp)
        self.mInputPortList.append(dstPortList)

    def isBuild(self):
        return self.mBuild

    def isPortExist(self, port):
        for portList in self.mInputPortList:
            for inputPort in portList:
                if inputPort.match(port):
                    return inputPort
        return None

    def getNodeList(self):
        return self.mNodeList

    def addNode(self, inputNode):
        # Utils.LogI(self.TAG, ("add %s" % (inputNode.getNodeName() + inputNode.getNodeInstanceId())))
        for node in self.mNodeList:
            if node.match(inputNode):
                return
        self.mNodeList.append(inputNode)

    def getDstPort(self, srcPort):
        return self.mPortLinkDes.get(srcPort)

    def getPortLink(self):
        return self.mPortLinkDes

    def addSrcNodeName(self, name):
        self.mSrcNodeNameList.append(name)

    def setPipelineName(self, pipelineName):
        self.mPipelineName = pipelineName

    def getPipelineName(self):
        return self.mPipelineName

    def setParentWidget(self, parent):
        self.mParentWidget = parent

    def addLevelNodePosMap(self, level, rect):
        if self.mLevelNodePosMap.get(level) is not None:
            rectList = self.mLevelNodePosMap.get(level)
            rectList.append(rect)
        else:
            rectList = [rect]
            temp = {level: rectList}
            self.mLevelNodePosMap.update(temp)

    def mergeLevelNodePosMap(self, level):
        '''
            Func: 合并gap小于50的segment
        '''
        removeList = []
        if self.mLevelNodePosMap.get(level) is not None:
            rectList = self.mLevelNodePosMap.get(level)
            rectList.sort(key=lambda x: x.y())
            for idx in range(0, len(rectList) - 1):
                preRect = rectList[idx]
                nextRect = rectList[idx + 1]
                gap = nextRect.y() - (preRect.y() + preRect.height())
                if gap < 50 and gap >= 0:
                    preRect.setHeight(preRect.height() + gap + nextRect.height())
                    removeList.append(nextRect)
                    # Utils.LogD(self.TAG, (sys._getframe().f_code.co_name, "pre:", preRect, "next:", nextRect, "gap", gap))
                elif gap < 0:
                    removeList.append(nextRect)
            for item in removeList:
                rectList.remove(item)

    def ajustNodeSize(self, inputNode, space, inputRect=None, second=False):
        '''
         调整 node 位置，算法原理：
         1. 记录level 对应 node 所占用的 pos segment，保存到list里，具体方法为第一个node的pos直接push到list里，后续进来的node先计算是否有覆盖
            如果有覆盖，则调整node位置，然后更新 level pos segment
         2. 对于与2个segment有冲突的情况，上移 y 坐标小的 segment 占用的所有node，包括 conflict node 也上移
         3. 有时候只与一个segment有冲突，但是调整位置后会与其他段有冲突，也是对 y 坐标小的segment上移
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        conflictMap = dict()

        if self.mLevelNodePosMap.get(inputNode.getNodeLevelKey()) is not None:
            inputPos = inputNode.getNodePos()
            inputSize = inputNode.getNodeSize()
            self.mergeLevelNodePosMap(inputNode.getNodeLevelKey())

            rectList = self.mLevelNodePosMap.get(inputNode.getNodeLevelKey())
            self.calOverlap(inputPos, inputSize, space, rectList, conflictMap, inputNode)
            confictOffsetList = list(conflictMap.keys())

            if len(confictOffsetList) == 2 and second == False:
                '''
                    1. 对于与2个segment有冲突的情况，上移 y 坐标小的 segment 占用的所有node，包括 conflict node 也上移
                    2. 上移完成后重新计算segment
                '''
                offset_0 = confictOffsetList[0]
                offset_1 = confictOffsetList[1]
                confictRect_0 = conflictMap.get(confictOffsetList[0])
                confictRect_1 = conflictMap.get(confictOffsetList[1])
                segment = confictRect_0 if confictRect_0.y() < confictRect_1.y() else confictRect_1
                conflictRectBottom = confictRect_0 if confictRect_0.y() > confictRect_1.y() else confictRect_1
                finalOffset = offset_0 if offset_0 < offset_1 else offset_1

                finalPos = QPoint(inputPos.x(), inputPos.y() + finalOffset)
                offset = -(abs(offset_0) + abs(offset_1))
                self.moveNode(segment, inputNode.getNodeLevelKey(), offset)
                inputNode.setNodePos(finalPos)
                segment.moveTopLeft(segment.topLeft() + QPoint(0, offset))
                segment.setHeight(inputSize.height() + inputNode.getNodePos().y() - segment.y())
                for rect in rectList:
                    if rect.y() < segment.y():
                        rect.moveTopLeft(rect.topLeft() + QPoint(0, offset))

                # Utils.LogD(self.TAG, ("%s: %s pos(%d, %d) --> pos(%d, %d), self offset %d, top node offset %d" % (
                #     sys._getframe().f_code.co_name, inputNode.getNodeName() + inputNode.getNodeInstanceId(),
                #     inputPos.x(), inputPos.y(), inputNode.getNodePos().x(), inputNode.getNodePos().y(), finalOffset, offset)))
            elif len(confictOffsetList) == 1 and second == False:
                '''
                    1. 只和一个segment冲突的情况，直接拿计算出的offset来做偏移
                    2. node偏移后需要在计算一次是否和其他segment又有了新的conflict，如果时在调用一边ajushNodeSize重新计算
                '''
                rect = conflictMap.get(confictOffsetList[0])
                finalPos = QPoint(inputPos.x(), inputPos.y() + confictOffsetList[0])
                inputNode.setNodePos(finalPos)

                # Utils.LogD(self.TAG, ("%s: %s pos(%d, %d) --> pos(%d, %d), self offset %d" % (
                #     sys._getframe().f_code.co_name, inputNode.getNodeName() + inputNode.getNodeInstanceId(),
                #     inputPos.x(), inputPos.y(), finalPos.x(), finalPos.y(), confictOffsetList[0])))

                conflictSecondMap = dict()
                self.calOverlap(inputNode.getNodePos(), inputSize, space, rectList, conflictSecondMap, inputNode)
                if len(conflictSecondMap.keys()) > 0:
                    # Utils.LogI(self.TAG, ("%s: %s There are still conflicts and nodes need to be adjusted" % (
                    #     sys._getframe().f_code.co_name, inputNode.getNodeName() + inputNode.getNodeInstanceId())))
                    self.ajustNodeSize(inputNode, space, rect, True)
                else:
                    if confictOffsetList[0] > 0:
                        # rect.setHeight(inputSize.height() + rect.height() + space)
                        rect.setHeight(inputSize.height() + inputNode.getNodePos().y() - rect.y())
                    else:
                        rect.setHeight(rect.y() - inputNode.getNodePos().y() + rect.height())
                        rect.moveTopLeft(QPoint(rect.x(), finalPos.y()))


            elif len(confictOffsetList) == 1 and second == True:
                '''
                    1. 调整位置后可能会与其他段有冲突，对 y 坐标小的所有segment上移
                    2. 偏移量就是通过 calOverlap 计算出来的，但是这里分两种情况：
                        1) offset < 0, 说明当前node下移时与下面的segment有冲突，所以Y小的segment上移offset
                        2) offset > 0, 说明当前node上移时与上面的segment有冲突，所以Y小的segment上移-offset, 当前conflict node不用上移
                '''
                conflitRect = conflictMap.get(confictOffsetList[0])
                if confictOffsetList[0] < 0:
                    self.moveNode(inputRect, inputNode.getNodeLevelKey(), confictOffsetList[0])
                else:
                    self.moveNode(conflitRect, inputNode.getNodeLevelKey(), -(confictOffsetList[0]))

                for rect in rectList:
                    if confictOffsetList[0] < 0:
                        if (rect.y() + rect.height()) <= (inputRect.y() + inputRect.height()):
                            rect.moveTopLeft(rect.topLeft() + QPoint(0, confictOffsetList[0]))
                            # Utils.LogD(self.TAG, ("%s: %s second ajust pos(%d, %d) self offset %d" % (
                            #     sys._getframe().f_code.co_name, inputNode.getNodeName() + inputNode.getNodeInstanceId(),
                            #     inputPos.x(), inputPos.y(), confictOffsetList[0]), "conflict Rect", inputRect, "moveNode Rect", rect))
                    else:
                        if (rect.y() + rect.height()) <= (conflitRect.y() + conflitRect.height()):
                            rect.moveTopLeft(rect.topLeft() - QPoint(0, confictOffsetList[0]))
                            # Utils.LogD(self.TAG, ("%s: %s second ajust pos(%d, %d) self offset %d" % (
                            #     sys._getframe().f_code.co_name, inputNode.getNodeName() + inputNode.getNodeInstanceId(),
                            #     inputPos.x(), inputPos.y(), confictOffsetList[0]), "conflict Rect", conflitRect, "moveNode Rect", rect))

                if confictOffsetList[0] < 0:
                    finalPos = QPoint(inputPos.x(), inputPos.y() + confictOffsetList[0])
                    inputNode.setNodePos(finalPos)
                    inputRect.setHeight(inputSize.height() + inputNode.getNodePos().y() - inputRect.y())
                else:
                    conflitRect.setHeight(inputSize.height() + inputNode.getNodePos().y() - conflitRect.y())
            else:
                rect = QRect(inputNode.getNodePos(), inputNode.getNodeSize())
                rectList.append(rect)
        else:
            rect = QRect(inputNode.getNodePos(), inputNode.getNodeSize())
            self.addLevelNodePosMap(inputNode.getNodeLevelKey(), rect)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def calOverlap(self, inputPos, inputSize, space, rectList, conflictMap, inputNode):
        for rect in rectList:
            xOffset, yOffset = self.calOverlapImplement(rect, inputPos, inputSize, space)
            # Utils.LogD(self.TAG, (
            # sys._getframe().f_code.co_name, ": node", inputNode.getNodeName() + inputNode.getNodeInstanceId(), "rect ",
            # rect, "inputPos", inputPos, "inputSize", inputSize, "offset: ", yOffset))
            if yOffset != 0:
                # Utils.LogD(self.TAG, (sys._getframe().f_code.co_name, ": ", rect, "offset: ", yOffset))
                temp = {yOffset: rect}
                conflictMap.update(temp)

    def calOverlapImplement(self, rect, inputPos, inputSize, space):
        xOffset = 0
        yOffset = 0

        if rect.x() < inputPos.x():
            temp = (rect.x() + rect.width()) - inputPos.x() > 0
            if temp > 0:
                xOffset = temp
        else:
            xOffset = (inputPos.x() + inputSize.width()) - rect.x()

        if rect.y() < inputPos.y():
            temp = (rect.y() + rect.height() + space) - inputPos.y()
            if temp >= 0:
                yOffset = temp
                # if yOffset > rect.height() / 2:
                #     yOffset = yOffset - rect.height() - inputSize.height() - space
                # else:
                #     yOffset = yOffset + space
        else:
            temp = -((inputPos.y() + inputSize.height() + space) - rect.y())
            if temp <= 0:
                yOffset = temp

        return xOffset, yOffset

    def moveNode(self, rect, level, offset):
        if self.mNodeLevelKeyMap.get(level) != None:
            for node in self.mNodeLevelKeyMap.get(level):
                pos = node.getNodePos()
                size = node.getNodeSize()
                if pos != None:
                    # Utils.LogD(self.TAG, ("%s: %s move y --> %d？ pos.y %d, rect.y %d" % (sys._getframe().f_code.co_name,
                    #         node.getNodeName() + node.getNodeInstanceId(), offset, pos.y(), rect.y())))
                    if offset < 0:
                        if (pos.y() + size.height()) <= (rect.y() + rect.height()):
                            node.setNodePos(pos + QPoint(0, offset))
                            # Utils.LogD(self.TAG, ("%s: %s y --> %d" % (sys._getframe().f_code.co_name,
                            #     node.getNodeName() + node.getNodeInstanceId(), offset)))
                    else:
                        if pos.y() >= rect.y():
                            node.setNodePos(pos + QPoint(0, offset))
                            # Utils.LogD(self.TAG, ("%s: %s y --> %d" % (sys._getframe().f_code.co_name,
                            #     node.getNodeName() + node.getNodeInstanceId(), offset)))

    def buildNode(self):
        '''
            @Func:
            1）设置srcNode的level
            2）port归属到node
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        for node in self.mNodeList:
            for outputPort in self.mPortLinkDes.keys():
                if self.matchNodePort(node, outputPort):
                    node.addOutputPort(outputPort)
                    tempLink = {outputPort: self.mPortLinkDes.get(outputPort)}
                    node.updateLink(tempLink)
                    # target buffer 作为 srcPort 的时候，需要被添加到mSrcNodeList
                    if outputPort.getPortName().find("TARGET") == 0:
                        node.setSourceNodeFlag(True)
                        node.setNodeLevel(0)
                        self.mSrcNodeList.append(node)
                    Utils.LogV(self.TAG, ("%s_IN_%s: add output prot %s" % (node.getNodeName(), node.getNodeInstanceId(), outputPort.getPortName())))
                for inputPort in self.mPortLinkDes.get(outputPort):
                    if self.matchNodePort(node, inputPort):
                        node.addInputPort(inputPort)
                        # Utils.LogV(self.TAG, ("%s_IN_%s: add input prot %s" % (
                        # node.getNodeName(), node.getNodeInstanceId(), outputPort.getPortName())))

        '''
            没有input Node 的全部都做为srcNode
        '''
        for node in self.mNodeList:
            need = True
            if len(node.getInputPort()) == 0:
                for srcNode in self.mSrcNodeList:
                    if node.match(srcNode) is True:
                        need = False
                if need:
                    node.setSourceNodeFlag(True)
                    node.setNodeLevel(0)
                    self.mSrcNodeList.append(node)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def createNodePos(self, point, fontSize):
        '''
        @Func:计算每个node的位置
        '''
        for node in self.mNodeList:
            link = node.getLink()
            for outputPort in link.keys():
                for inputPort in link.get(outputPort):
                    for child in self.mNodeList:
                        if self.matchNodePort(child, inputPort):
                            # Utils.LogV(self.TAG, ("%s_IN_%s: input prot %s, child %s_IN_%s output %s" % (
                            #     node.getNodeName(), node.getNodeInstanceId(), inputPort.getPortName(),
                            #     child.getNodeName(), child.getNodeInstanceId(), outputPort.getPortName())))
                            node.updateChildNodePortMap(child, outputPort)
                            child.updateParentNodePortMap(node, inputPort)

        self.calNodePosNew(point, fontSize)
        self.mBuild = True

    def calNodePosNew(self, centerPos, fontSize):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        i = 0
        preNodeY = centerPos.y()
        preNodeHeight = 0
        self.mFont = QFont()
        '''
            先确定srcNode的位置，childNode根据srcNode位置来确定
        '''
        for srcNode in self.mSrcNodeList:
            referencePoint = QPoint(centerPos.x(), preNodeHeight + preNodeY + 50)
            srcNode.calNodeSize()
            srcNode.sortOutputPort()

            if srcNode.getNodePos() == None:
                srcNode.setNodePos(referencePoint)

            if srcNode.getNodeFontSize() != None:
                self.mFont.setPixelSize(srcNode.getNodeFontSize() - 6)
            else:
                self.mFont.setPixelSize(fontSize - 6)

            srcNode.calOutputPortPosNew(self.mFont)
            srcList = srcNode.getChildNodeSortList()
            for child in srcList:
                nextLevelKey = self.getNextNodeLevelKey(srcNode.getNodeLevelKey())
                if child.getNodeLevelKey() == nextLevelKey or nextLevelKey == 999:
                    self.calChildNodePosNew(child, srcNode, srcNode.getChildNodePortMap().get(child), nextLevelKey)
            i += 1
            preNodeY = srcNode.getNodePos().y()
            preNodeHeight = srcNode.getNodeSize().height()

        for node in self.mNodeList:
            node.calInputPortPos(self.mFont)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def calChildNodePosNew(self, currentNode, parent, outputPortList, currentLevelKey=None):
        '''
            @Func：根据parent Node的位置计算child Node的位置，并且递归调用计算完所有的符合要求的node child Node
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        if currentNode.getNodePos() == None:
            parentNodePos = parent.getNodePos()
            parentNodeSize = parent.getNodeSize()
            firstPortPos = outputPortList[0].getPortPos()
            currentNode.calNodeSize()
            referencePoint = QPoint(parentNodePos.x() + parentNodeSize.width() + 200,
                                    parentNodePos.y() + firstPortPos.y() - int(currentNode.getNodeSize().height() / 2))
            Utils.LogD(self.TAG, ("%s: -- " % (sys._getframe().f_code.co_name)))
            currentNode.sortOutputPort()
            currentNode.setNodePos(referencePoint)
            self.ajustNodeSize(currentNode, 50)
            # Utils.LogD(self.TAG, ("%s:currentLevelKey %d current %s key %d" %
            #                       (sys._getframe().f_code.co_name, currentLevelKey,
            #                        currentNode.getNodeName() + currentNode.getNodeInstanceId(),
            #                        currentNode.getNodeLevelKey()), "ref", referencePoint, "ajust ref", currentNode.getNodePos()))
            currentNode.calOutputPortPosNew(self.mFont)
            # currentNode.calInputPortPos()
            for child in currentNode.getChildNodeSortList():
                nextLevelKey = self.getNextNodeLevelKey(currentLevelKey)
                # Utils.LogD(self.TAG, ("%s:currentLevelKey %d parent %s level %d, child %s level %d, getNext %d" %
                #     (sys._getframe().f_code.co_name, currentLevelKey,
                #     currentNode.getNodeName() + currentNode.getNodeInstanceId(), currentNode.getNodeLevelKey(),
                #     child.getNodeName() + child.getNodeInstanceId(), child.getNodeLevelKey(), nextLevelKey)))
                # if child.getNodeLevelKey() == nextLevelKey or child.getNodeLevelKey() == currentLevelKey or nextLevelKey == 999:
                '''
                    child node 的level必须是下一级level才会计算，主要是为了同一级的放在同一列上，后面计算同一列覆盖情况时才不会出现bug
                '''
                if child.getNodeLevelKey() == nextLevelKey or nextLevelKey == 999:
                    self.calChildNodePosNew(child, currentNode, currentNode.getChildNodePortMap().get(child),
                                            nextLevelKey)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def createLevel(self):
        '''
            @Func:给node定义level
            @原理:通过link可以确认node的topology关系，由于之前我们已经确认了srcNode，所以遍历srcNode，实际上也就是找到level为0的node
            然后找的其所有的child node并设置child node为下一级，对于有多重level的后面在计算node pos时按照最大的来处理
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        level = 1
        while True:
            if self.addLevel(level) is False:
                break
            level += 1

        # 检查一下有没有node没有设置等级，不然下面排序的时候会crash
        for node in self.mNodeList:
            if len(node.getNodeLevel()) <= 0:
                QMessageBox.warning(self.mParentWidget, "Warning", "An error has occurred!")
                Utils.LogE(self.TAG, ("%s: %s level len is %d" % (
                sys._getframe().f_code.co_name, node.getNodeName() + node.getNodeInstanceId() + node.getTargetName(),
                len(node.getNodeLevel()))))
                exit(0)

        # 重新排序
        self.mNodeList.sort(key=lambda x: x.getNodeLevel()[0])
        self.mMaxLevel = level - 1
        self.createNodeLevelMap()
        Utils.LogD(self.TAG, ("%s: -" % (sys._getframe().f_code.co_name)))

    # 给node分等级
    def addLevel(self, level):
        Utils.LogV(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        inputPortList = []
        findParent = False
        parentNodeSet = set()
        # level = 1 的时候说明需要找第一级 node，所以只需要拿sourceNode 的 output 对应的input
        if level == 1:
            # parentNode = self.mSrcNodeList[0]
            for outputPort in self.mPortLinkDes.keys():
                for srcNode in self.mSrcNodeList:
                    if self.matchNodePort(srcNode, outputPort):
                        parentNodeSet.add(srcNode)
                        inputPortList.append(self.mPortLinkDes.get(outputPort))
            findParent = True
        # 先找到level-1的node，拿到 level-1 node 的 output 对应的input
        else:
            for node in self.mNodeList:
                if len(node.getNodeLevel()) > 0:
                    if node.getNodeLevel()[0] == level - 1:
                        # Utils.LogD(self.TAG,
                        #            ("%s: parentNode %s, level %d" % (sys._getframe().f_code.co_name,
                        #                                              node.getNodeName() + node.getNodeInstanceId(),
                        #                                              node.getNodeLevel()[0])))
                        parentNodeSet.add(node)
                        findParent = True
                        for outputPort in self.mPortLinkDes.keys():
                            if self.matchNodePort(node, outputPort):
                                need = True
                                for inputPort in self.mPortLinkDes.get(outputPort):
                                    if self.matchNodePort(node, inputPort):
                                        need = False
                                if need:
                                    inputPortList.append(self.mPortLinkDes.get(outputPort))
        # 根据inputnode设置node的level
        for inputPort in inputPortList:
            for port in inputPort:
                for node in self.mNodeList:
                    if self.matchNodePort(node, port):
                        node.setNodeLevel(level)
                        # Utils.LogD(self.TAG,
                        #            ("%s: child %s, level %d" % (sys._getframe().f_code.co_name,
                        #                                         node.getNodeName() + node.getNodeInstanceId(),
                        #                                         node.getNodeLevel()[0])))
                        # if node.getNodeLevel() < 0:
        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return findParent

    def getMaxLevel(self):
        return self.mMaxLevel

    def calNodeKey(self, levelList):
        key = 1
        if len(levelList) == 1:
            key = levelList[0] * levelList[0]
        else:
            # for level in levelList:
            #     key *= level
            '''
                pipeline@2:
                D : PipelineDes : calChildNodePosNew:currentLevelKey 9 parent FDManager0 level 9, child SinkNoBuffer4 level 9, getNext 16
                如果按照下面这样写且setNodeLevel时不排序的话会导致 parentNode 与 children 同级
            '''
            key = levelList[0] * levelList[0]
        return key

    def createNodeLevelMap(self):
        for node in self.mNodeList:
            '''
                Pipeline@1：
                D : PipelineDes : calChildNodePosNew:currentLevelKey 4 parent BPS0 level 4, child IPE1 level 9, getNext 6
                问题：
                这里从大到小排序以及计算key时按照最大的level计算原因是在计算pos时如果parentNode的childNode有断层，会导致有些node没有去计算pos
                比如 parent BPS0 level 4, child IPE1 level 9, nextLevel 6，那么IPE1将不会被计算node
            '''
            node.sortLevelList()
            node.calNodeSize()
            key = self.calNodeKey(node.getNodeLevel())
            node.setNodeLevelKey(key)
            # Utils.LogD(self.TAG,
            #            ("%s: node %s, key %d, " % (sys._getframe().f_code.co_name,
            #                                         node.getNodeName() + node.getNodeInstanceId(),
            #                                         node.getNodeLevelKey())))
            if self.mNodeLevelKeyMap.get(key) is None:
                temp = {key: [node]}
                self.mNodeLevelKeyMap.update(temp)
            else:
                self.mNodeLevelKeyMap.get(key).append(node)

        self.mNodeLevelKeyList = list(self.mNodeLevelKeyMap.keys())
        self.mNodeLevelKeyList.sort()

    def getNextNodeLevelKey(self, key):
        for idx in range(0, len(self.mNodeLevelKeyList)):
            if self.mNodeLevelKeyList[idx] == key:
                if idx == len(self.mNodeLevelKeyList) - 1:
                    return 999
                else:
                    return self.mNodeLevelKeyList[idx + 1]
        return -1

    def calNodePosLegacy(self, centerPos):
        '''
        # 遗留的计算node pos的方法。算法原理是通过level等级来布局，没有考虑到port之间的交叉
        # 以及当前node是否靠近parent node的相关outputPort 会导致布线交叉较多
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.createNodeLevelMap()
        i = 0
        horizontalInterval = 200
        referencePoint = QPoint(centerPos.x(), centerPos.y())
        previousHeight = 0
        keyList = list(self.mNodeLevelKeyMap.keys())
        keyList.sort()
        offsetMap = dict()
        nodeMaxWidth = 0
        for key in keyList:
            j = 0
            previousHeight = 0
            horizontalPoint = QPoint(referencePoint.x() + 200 + nodeMaxWidth, referencePoint.y())
            tempPos = QPoint(horizontalPoint)
            nodeMaxWidth = 0
            for node in self.mNodeLevelKeyMap.get(key):
                horizontalPoint += QPoint(0, previousHeight + 50)
                node.setNodePos(QPoint(horizontalPoint))
                if node.getNodePos() != None:
                    Utils.LogV(self.TAG,
                               ("%s: pre %d j %d pos %d, %d" % (
                               node.getNodeName(), previousHeight, j, node.getNodePos().x(), node.getNodePos().y())))
                previousHeight = node.getNodeSize().height()
                if nodeMaxWidth < node.getNodeSize().width():
                    nodeMaxWidth = node.getNodeSize().width()
                j += 1
            referencePoint.setX(horizontalPoint.x())
            tempOffset = {key: QPoint(horizontalPoint - tempPos)}
            offsetMap.update(tempOffset)

            i += 1

        # 调整布局向上移动整个level的一般，使其中间部分与sensor node对其
        for key in keyList:
            if offsetMap.get(key) != None:
                Utils.LogE(self.TAG,
                           ("%s: offsetMap key %d is %d " % (
                           sys._getframe().f_code.co_name, key, len(self.mNodeLevelKeyMap.get(key)))))
                # 当前level有多个node的情况
                if offsetMap.get(key).y() > 0:
                    offset = int(offsetMap.get(key).y() / 2)
                    for node in self.mNodeLevelKeyMap.get(key):
                        # Utils.LogD(self.TAG,
                        #            ("ttt%s: pre %d j %d pos %d, %d" % (
                        #            node.getNodeName(), previousHeight, j, test.x(), test.y())))
                        node.setNodePos(node.getNodePos() - QPoint(0, offset))
                if len(self.mNodeLevelKeyMap.get(key)) == 1:
                    node = self.mNodeLevelKeyMap.get(key)[0]
                    offset = node.getNodeSize().height() / 2
                    node.setNodePos(node.getNodePos() - QPoint(0, offset))
                    Utils.LogE(self.TAG, ("%s: offsetMap key %d is %s " % (
                    sys._getframe().f_code.co_name, key, node.getNodeName())))
            else:
                Utils.LogE(self.TAG, ("%s: offsetMap key %d is none " % (sys._getframe().f_code.co_name, key)))

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def matchNodePort(self, node, port):
        result = False
        if node.getNodeId() == port.getNodeId() and node.getNodeInstanceId() == port.getNodeInstanceId():
            result = True
        if node.isTargetNode() and port.isTargetPort():
            if node.getTargetName().find(port.getPortName()) < 0:
                result = False
        return result

    def print(self):
        Utils.LogD("  ", ("---------------- %s ---------------- " % (self.mPipelineName)))
        for node in self.mNodeList:
            # Utils.LogD("  ", ("nodeLength %d" % (len(self.mNodeList))))
            node.print()

        for srcNode in self.mSrcNodeNameList:
            msg = ("sourceNode: %s" % (srcNode))
            Utils.LogD("    ", msg)
