from Utils import Utils
from PyQt5.Qt import QPoint
from PyQt5.Qt import QFont
from PyQt5.Qt import QRect
from PyQt5.Qt import QMessageBox
from LayoutEngine import LayoutEngine
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

    def buildNode(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        for node in self.mNodeList:
            for outputPort in self.mPortLinkDes.keys():
                if self.matchNodePort(node, outputPort):
                    node.addOutputPort(outputPort)
                    tempLink = {outputPort: self.mPortLinkDes.get(outputPort)}
                    node.updateLink(tempLink)
                    if outputPort.getPortName().find("TARGET") == 0:
                        node.setSourceNodeFlag(True)
                        node.setNodeLevel(0)
                        self.mSrcNodeList.append(node)
                    Utils.LogV(self.TAG, ("%s_IN_%s: add output prot %s" % (node.getNodeName(), node.getNodeInstanceId(), outputPort.getPortName())))
                for inputPort in self.mPortLinkDes.get(outputPort):
                    if self.matchNodePort(node, inputPort):
                        node.addInputPort(inputPort)

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
        for node in self.mNodeList:
            link = node.getLink()
            for outputPort in link.keys():
                for inputPort in link.get(outputPort):
                    for child in self.mNodeList:
                        if self.matchNodePort(child, inputPort):
                            node.updateChildNodePortMap(child, outputPort)
                            child.updateParentNodePortMap(node, inputPort)

        layout_engine = LayoutEngine(self)
        layout_engine.compute_layout(point, fontSize)

    def createLevel(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        level = 1
        while True:
            if self.addLevel(level) is False:
                break
            level += 1

        for node in self.mNodeList:
            if len(node.getNodeLevel()) <= 0:
                Utils.LogE(self.TAG, ("%s: %s level len is %d" % (
                sys._getframe().f_code.co_name, node.getNodeName() + node.getNodeInstanceId() + node.getTargetName(),
                len(node.getNodeLevel()))))

        self.mNodeList.sort(key=lambda x: x.getNodeLevel()[0])
        self.mMaxLevel = level - 1
        self.createNodeLevelMap()
        Utils.LogD(self.TAG, ("%s: -" % (sys._getframe().f_code.co_name)))

    def addLevel(self, level):
        Utils.LogV(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        inputPortList = []
        findParent = False
        parentNodeSet = set()
        if level == 1:
            for outputPort in self.mPortLinkDes.keys():
                for srcNode in self.mSrcNodeList:
                    if self.matchNodePort(srcNode, outputPort):
                        parentNodeSet.add(srcNode)
                        inputPortList.append(self.mPortLinkDes.get(outputPort))
            findParent = True
        else:
            for node in self.mNodeList:
                if len(node.getNodeLevel()) > 0:
                    if node.getNodeLevel()[0] == level - 1:
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
        for inputPort in inputPortList:
            for port in inputPort:
                for node in self.mNodeList:
                    if self.matchNodePort(node, port):
                        node.setNodeLevel(level)
        Utils.LogV(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return findParent

    def getMaxLevel(self):
        return self.mMaxLevel

    def calNodeKey(self, levelList):
        key = 1
        if len(levelList) == 1:
            key = levelList[0] * levelList[0]
        else:
            key = levelList[0] * levelList[0]
        return key

    def createNodeLevelMap(self):
        for node in self.mNodeList:
            node.sortLevelList()
            node.calNodeSize()
            key = self.calNodeKey(node.getNodeLevel())
            node.setNodeLevelKey(key)
            if self.mNodeLevelKeyMap.get(key) is None:
                temp = {key: [node]}
                self.mNodeLevelKeyMap.update(temp)
            else:
                self.mNodeLevelKeyMap.get(key).append(node)

        self.mNodeLevelKeyList = list(self.mNodeLevelKeyMap.keys())
        self.mNodeLevelKeyList.sort()

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
            node.print()

        for srcNode in self.mSrcNodeNameList:
            msg = ("sourceNode: %s" % (srcNode))
            Utils.LogD("    ", msg)
