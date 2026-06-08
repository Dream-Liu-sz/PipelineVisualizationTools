
import xml.etree.ElementTree as ET
from Node import NodeDes
from Port import PortDes
from Pipeline import PipelineDes
from Utils import Utils
import sys

class UseCaseDes(object):
    TAG = "UseCaseDes"
    mFileName = ""
    mRoot = None

    def __init__(self, fileName):
        self.mFileName = fileName
        self.mUseCasePipelineMap = dict()
        self.mParent = None

    def useCaseTranslation(self):
        '''
            @Func:解析useCase
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        try:
            tree = ET.parse(self.mFileName)

            # 获得根节点
            self.mRoot = tree.getroot()

        except Exception as e:
            Utils.LogE(self.TAG, ("parse " + self.mFileName + " failed!"))

        useCaseList = self.mRoot.findall("Usecase")
        for useCase in useCaseList:
            useCasePipelineNameList = []
            useCaseNameList = useCase.findall("UsecaseName")
            self.pipelineTranslation(useCase, useCasePipelineNameList)
            temp = {useCaseNameList[0].text: useCasePipelineNameList}
            self.mUseCasePipelineMap.update(temp)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def pipelineTranslation(self, useCase, pipelineListAll):
        '''
            @Func:解析pipeline
        '''
        pipelineList = useCase.findall("Pipeline")
        if len(pipelineList) < 1:
            Utils.LogE(self.TAG, "pipelineList length < 1")

        for pipeline in pipelineList:
            pipelineDes = PipelineDes()
            pipelineNameList = pipeline.findall("PipelineName")
            if len(pipelineNameList) == 1:
                pipelineDes.setPipelineName(pipelineNameList[0].text)
            else:
                Utils.LogE(self.TAG, "pipelineNameList length is not 1")

            # Utils.LogI(self.TAG, ("pipeline %s:" % (pipelineDes.getPipelineName())))
            self.nodesTranslation(pipeline, pipelineDes)
            self.portTranslation(pipeline, pipelineDes)
            self.addMissNode(pipelineDes)

            pipelineListAll.append(pipelineDes)

    def nodesTranslation(self, pipeline, pipelineDes):
        '''
            @Func:解析Node
        '''
        nodesList = pipeline.findall("NodesList")
        if len(nodesList) < 1:
            Utils.LogE(self.TAG, "pipelineList length < 1")

        for nodes in nodesList:
            nodeList = nodes.findall("Node")
            for node in nodeList:
                nodeDes = NodeDes(node.findall("NodeName")[0].text,
                                  node.findall("NodeId")[0].text,
                                  node.findall("NodeInstance")[0].text,
                                  node.findall("NodeInstanceId")[0].text)
                pipelineDes.addNode(nodeDes)

                nodePropertyList = node.findall("NodeProperty")
                for nodeProp in nodePropertyList:
                    nodePropertyName = nodeProp.findall("NodePropertyName")[0].text if len(nodeProp.findall("NodePropertyName")) != 0 else "None"
                    nodePropertyId = nodeProp.findall("NodePropertyId")[0].text if len(nodeProp.findall("NodePropertyId")) != 0 else "None"
                    nodePropertyDataType = nodeProp.findall("NodePropertyDataType")[0].text if len(nodeProp.findall("NodePropertyDataType")) != 0 else "None"
                    nodePropertyValue = nodeProp.findall("NodePropertyValue")[0].text if len(nodeProp.findall("NodePropertyValue")) != 0 else "None"

                    nodeDes.setNodePorp(nodePropertyName, nodePropertyId, nodePropertyDataType, nodePropertyValue)

    def portTranslation(self, pipeline, pipelineDes):
        portLinkagesList = pipeline.findall("PortLinkages")
        if len(portLinkagesList) < 1:
            Utils.LogE(self.TAG, "portLinkages length < 1")

        for portLinkages in portLinkagesList:
            sourceNodeList = portLinkages.findall("SourceNode")
            targetNameList = portLinkages.findall("TargetName")

            for sourceNode in sourceNodeList:
                pipelineDes.addSrcNodeName(sourceNode.text)

                # Utils.LogV(self.TAG, ("add source %s" % (sourceNode.text)))

            for targetName in targetNameList:
                pipelineDes.addSrcNodeName(targetName.text)
                # Utils.LogV(self.TAG, ("add targe %s" % (targetName.text)))

            linkList = portLinkages.findall("Link")
            for port in linkList:
                srcPortList = port.findall("SrcPort")
                portName = srcPortList[0].findall("PortName")[0].text
                portId = srcPortList[0].findall("PortId")[0].text
                nodeName = srcPortList[0].findall("NodeName")[0].text
                nodeId = srcPortList[0].findall("NodeId")[0].text
                nodeInstance = srcPortList[0].findall("NodeInstance")[0].text
                nodeInstanceId = srcPortList[0].findall("NodeInstanceId")[0].text
                srcPortDes = PortDes(portName, portId, nodeName, nodeId, nodeInstance, nodeInstanceId)
                # target 做为 srcNode 时，需要认为其时一个node
                if portName.find("TARGET") == 0:
                    nodeDes = NodeDes(nodeName, nodeId, nodeInstance, nodeInstanceId, portName)
                    # nodeDes.setTargetNode(True)
                    pipelineDes.addNode(nodeDes)
                # Utils.LogV(self.TAG, ("find src %s_%s" % (srcPortList[0].findall("PortName")[0].text, srcPortList[0].findall("PortId")[0].text)))

                dstPortList = port.findall("DstPort")
                dstPortListAll = []
                for dstPort in dstPortList:
                    portName = dstPort.findall("PortName")[0].text
                    portId = dstPort.findall("PortId")[0].text
                    nodeName = dstPort.findall("NodeName")[0].text
                    nodeId = dstPort.findall("NodeId")[0].text
                    nodeInstance = dstPort.findall("NodeInstance")[0].text
                    nodeInstanceId = dstPort.findall("NodeInstanceId")[0].text

                    dstPortDes = PortDes(portName, portId, nodeName, nodeId, nodeInstance, nodeInstanceId)
                    '''
                    # 判断这个port是否已经被添加，如果是会返回这个port的实例，然后被添加到另一组outputPort --> inputPort中
                    # 这样做的原因是相同portId nodeId nodeInstanceId 的 port只需要一个实例，不然后面match的时候会出问题
                    '''
                    onlyPortInstance = pipelineDes.isPortExist(dstPortDes)
                    if onlyPortInstance == None:
                        dstPortListAll.append(dstPortDes)
                    else:
                        dstPortListAll.append(onlyPortInstance)


                    # TARGET BUFFER Port 也作为 node
                    if portName.find("TARGET") == 0:
                        dstPortDes.setTargetPort(True)
                        nodeDes = NodeDes(nodeName, nodeId, nodeInstance, nodeInstanceId, portName)
                        nodeDes.setTargetNode(True)
                        pipelineDes.addNode(nodeDes)
                pipelineDes.updatePortToProtMap(srcPortDes, dstPortListAll)

    def addMissNode(self, pipeline):
        '''
            @Func:有些pipeline，link上的port使用了nodeList中没有的Node，需要把这些node也添加进来
        '''
        nodeList = pipeline.getNodeList()
        portLink = pipeline.getPortLink()

        for outputPort in portLink.keys():
            need = True
            for node in nodeList:
                if pipeline.matchNodePort(node, outputPort) == True:
                    need = False

            if need:
                # Utils.LogD(self.TAG, ("%s:  %s add %s , find not %s" % (sys._getframe().f_code.co_name,
                #     pipeline.getPipelineName(), outputPort.getNodeName() + outputPort.getNodeInstanceId(),
                #     outputPort.getPortName() + outputPort.getPortId())))
                nodeDes = NodeDes(outputPort.getNodeName(),
                                  outputPort.getNodeId(),
                                  outputPort.getNodeInstance(),
                                  outputPort.getNodeInstanceId())
                pipeline.addNode(nodeDes)
            for inputPort in portLink.get(outputPort):
                need = True
                for node in nodeList:
                    if pipeline.matchNodePort(node, inputPort) == True:
                        need = False
                if need:
                    # Utils.LogD(self.TAG, ("%s:  %s add %s , find not %s" % (sys._getframe().f_code.co_name,
                    #                                                         pipeline.getPipelineName(),
                    #                                                         inputPort.getNodeName() + inputPort.getNodeInstanceId(),
                    #                                                         inputPort.getPortName() + inputPort.getPortId())))
                    nodeDes = NodeDes(inputPort.getNodeName(),
                                      inputPort.getNodeId(),
                                      inputPort.getNodeInstance(),
                                      inputPort.getNodeInstanceId())
                    pipeline.addNode(nodeDes)

    def buildPipeline(self, useCase, pipelineName, point, fontSize, parentWidget):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        pipelineList = self.mUseCasePipelineMap.get(useCase)
        for pipeline in pipelineList:
            if pipeline.getPipelineName() == pipelineName:
                if pipeline.isBuild() is False:
                    pipeline.setParentWidget(parentWidget)
                    pipeline.buildNode()
                    pipeline.createLevel()
                    pipeline.createNodePos(point, fontSize)
                return pipeline

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        return None

    def getPipelineMap(self):
        return self.mUseCasePipelineMap

    def print(self):
        for key in self.mUseCasePipelineMap.keys():
            Utils.LogD("", ("----------------- %s -----------------" % (str(key))))
            for pipeline in self.mUseCasePipelineMap.get(key):
                pipeline.print()