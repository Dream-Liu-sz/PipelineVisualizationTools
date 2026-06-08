import networkx as nx
from PyQt5.Qt import QPoint, QSize, QFont, QFontMetrics, QRect
from Utils import Utils
import sys


class LayoutEngine:
    TAG = "LayoutEngine"
    LAYER_SPACING = 150
    NODE_SPACING = 28
    MIN_NODE_WIDTH = 190
    MIN_NODE_HEIGHT = 82

    def __init__(self, pipeline):
        self.mPipeline = pipeline
        self.mGraph = nx.DiGraph()
        self.mLayers = {}
        self.mLayerList = []
        self.mNodeOrder = {}
        self.mFont = QFont()

    def compute_layout(self, center_pos, font_size):
        self.mFont.setPixelSize(font_size - 6)
        self.build_graph()

        if self.mGraph.number_of_nodes() == 0:
            self.mPipeline.mBuild = True
            return

        if self.mGraph.number_of_nodes() == 1:
            node_id = list(self.mGraph.nodes())[0]
            node = self.mGraph.nodes[node_id]['node']
            node.calNodeSize()
            node.setNodePos(center_pos)
            node.sortOutputPort()
            node.calOutputPortPosNew(self.mFont)
            node.calInputPortPos(self.mFont)
            self.mPipeline.mBuild = True
            return

        self.assign_layers()
        self.minimize_crossings()
        self.position_nodes(center_pos)
        self.order_ports()
        self.mPipeline.mBuild = True

    def build_graph(self):
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        self.mGraph.clear()

        added_nodes = set()
        for node in self.mPipeline.getNodeList():
            node_id = self._node_key(node)
            if node_id not in added_nodes:
                self.mGraph.add_node(node_id, node=node)
                added_nodes.add(node_id)

        port_link = self.mPipeline.getPortLink()
        for src_port, dst_ports in port_link.items():
            src_node_id = self._find_node_key_for_port(src_port)
            if src_node_id is None:
                continue
            for dst_port in dst_ports:
                dst_node_id = self._find_node_key_for_port(dst_port)
                if dst_node_id is None:
                    continue
                if src_node_id != dst_node_id:
                    if not self.mGraph.has_edge(src_node_id, dst_node_id):
                        self.mGraph.add_edge(src_node_id, dst_node_id,
                                             src_ports=[src_port], dst_ports=[dst_port])
                    else:
                        edge_data = self.mGraph[src_node_id][dst_node_id]
                        if src_port not in edge_data['src_ports']:
                            edge_data['src_ports'].append(src_port)
                        if dst_port not in edge_data['dst_ports']:
                            edge_data['dst_ports'].append(dst_port)

        for node_id in list(self.mGraph.nodes()):
            if self.mGraph.in_degree(node_id) == 0:
                node = self.mGraph.nodes[node_id]['node']
                node.setSourceNodeFlag(True)
                node.setNodeLevel(0)

        for node in self.mPipeline.getNodeList():
            node_id = self._node_key(node)
            if node_id not in self.mGraph:
                self.mGraph.add_node(node_id, node=node)

        Utils.LogD(self.TAG, ("%s: - nodes=%d edges=%d" % (
            sys._getframe().f_code.co_name, self.mGraph.number_of_nodes(), self.mGraph.number_of_edges())))

    def _find_node_key_for_port(self, port):
        for node in self.mPipeline.getNodeList():
            if self.mPipeline.matchNodePort(node, port):
                return self._node_key(node)
        port_key = self._port_node_key(port)
        if port_key in self.mGraph:
            return port_key
        for node_id in self.mGraph.nodes():
            if 'node' in self.mGraph.nodes[node_id]:
                node = self.mGraph.nodes[node_id]['node']
                if node.getNodeId() == port.getNodeId() and node.getNodeInstanceId() == port.getNodeInstanceId():
                    return node_id
        return None

    def _node_key(self, node):
        return node.getNodeName() + "_" + node.getNodeInstanceId()

    def _port_node_key(self, port):
        return port.getNodeName() + "_" + port.getNodeInstanceId()

    def assign_layers(self):
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        self.mLayers = {}

        if self.mGraph.number_of_nodes() == 0:
            return

        if not nx.is_directed_acyclic_graph(self.mGraph):
            Utils.LogE(self.TAG, ("%s: graph has cycles, falling back to simple layering" % (
                sys._getframe().f_code.co_name)))
            self._assign_layers_simple()
            return

        for node_id in nx.topological_sort(self.mGraph):
            predecessors = list(self.mGraph.predecessors(node_id))
            if not predecessors:
                self.mLayers[node_id] = 0
            else:
                self.mLayers[node_id] = max(self.mLayers[p] for p in predecessors) + 1

        self._build_layer_list()

        for node_id, layer in self.mLayers.items():
            node = self.mGraph.nodes[node_id]['node']
            node.setNodeLevel(layer)
            node.setNodeLevelKey(self._layer_key(layer))

        Utils.LogD(self.TAG, ("%s: - max_layer=%d" % (
            sys._getframe().f_code.co_name, len(self.mLayerList) - 1 if self.mLayerList else 0)))

    def _assign_layers_simple(self):
        visited = set()
        queue = []
        for node_id in self.mGraph.nodes():
            if self.mGraph.in_degree(node_id) == 0:
                self.mLayers[node_id] = 0
                queue.append(node_id)
                visited.add(node_id)

        while queue:
            current = queue.pop(0)
            for successor in self.mGraph.successors(current):
                if successor not in visited:
                    self.mLayers[successor] = self.mLayers[current] + 1
                    visited.add(successor)
                    queue.append(successor)

        for node_id in self.mGraph.nodes():
            if node_id not in self.mLayers:
                self.mLayers[node_id] = 0

        self._build_layer_list()

    def _build_layer_list(self):
        max_layer = max(self.mLayers.values()) if self.mLayers else 0
        self.mLayerList = [[] for _ in range(max_layer + 1)]
        for node_id, layer in self.mLayers.items():
            self.mLayerList[layer].append(node_id)

    def _layer_key(self, layer):
        return layer * layer

    def minimize_crossings(self, iterations=24):
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        if len(self.mLayerList) <= 1:
            return

        best_order = [list(layer) for layer in self.mLayerList]
        best_crossings = self._count_crossings(best_order)

        for i in range(iterations):
            if i % 2 == 0:
                self._sweep_down(best_order)
            else:
                self._sweep_up(best_order)

            current_crossings = self._count_crossings(best_order)
            if current_crossings < best_crossings:
                best_crossings = current_crossings
                self.mLayerList = [list(layer) for layer in best_order]

        self.mNodeOrder = {}
        for layer_idx, layer in enumerate(self.mLayerList):
            for pos, node_id in enumerate(layer):
                self.mNodeOrder[node_id] = pos

        Utils.LogD(self.TAG, ("%s: - best_crossings=%d" % (
            sys._getframe().f_code.co_name, best_crossings)))

    def _sweep_down(self, layers):
        for i in range(1, len(layers)):
            pos_map = {node_id: idx for idx, node_id in enumerate(layers[i - 1])}
            barycenters = {}
            for node_id in layers[i]:
                predecessors = list(self.mGraph.predecessors(node_id))
                if predecessors:
                    positions = [pos_map.get(p, 0) for p in predecessors if p in pos_map]
                    barycenters[node_id] = sum(positions) / len(positions) if positions else 0
                else:
                    barycenters[node_id] = 0
            layers[i] = sorted(layers[i], key=lambda n: barycenters[n])

    def _sweep_up(self, layers):
        for i in range(len(layers) - 2, -1, -1):
            pos_map = {node_id: idx for idx, node_id in enumerate(layers[i + 1])}
            barycenters = {}
            for node_id in layers[i]:
                successors = list(self.mGraph.successors(node_id))
                if successors:
                    positions = [pos_map.get(s, 0) for s in successors if s in pos_map]
                    barycenters[node_id] = sum(positions) / len(positions) if positions else 0
                else:
                    barycenters[node_id] = 0
            layers[i] = sorted(layers[i], key=lambda n: barycenters[n])

    def _count_crossings(self, layers):
        crossings = 0
        for i in range(len(layers) - 1):
            upper = layers[i]
            lower = layers[i + 1]
            upper_pos = {node_id: idx for idx, node_id in enumerate(upper)}
            lower_pos = {node_id: idx for idx, node_id in enumerate(lower)}

            edge_targets = []
            for u_idx, u_node in enumerate(upper):
                targets = []
                for v_node in self.mGraph.successors(u_node):
                    if v_node in lower_pos:
                        targets.append(lower_pos[v_node])
                targets.sort()
                for t in targets:
                    edge_targets.append((u_idx, t))

            for j in range(len(edge_targets)):
                for k in range(j + 1, len(edge_targets)):
                    if edge_targets[j][1] > edge_targets[k][1]:
                        crossings += 1
        return crossings

    def position_nodes(self, center_pos):
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        if not self.mLayerList:
            return

        layer_widths = []
        for layer in self.mLayerList:
            max_width = self.MIN_NODE_WIDTH
            for node_id in layer:
                node = self.mGraph.nodes[node_id]['node']
                node.calNodeSize()
                if node.getNodeSize().width() > max_width:
                    max_width = node.getNodeSize().width()
            layer_widths.append(max_width)

        x_offset = center_pos.x()
        for layer_idx, layer in enumerate(self.mLayerList):
            total_height = 0
            node_sizes = []
            for node_id in layer:
                node = self.mGraph.nodes[node_id]['node']
                node.calNodeSize()
                size = node.getNodeSize()
                node_sizes.append(size)
                total_height += size.height()
            total_height += self.NODE_SPACING * max(0, len(layer) - 1)

            y = center_pos.y() - total_height / 2

            for idx, node_id in enumerate(layer):
                node = self.mGraph.nodes[node_id]['node']
                node_x = x_offset
                node_y = y
                node.setNodePos(QPoint(int(node_x), int(node_y)))
                node.sortOutputPort()
                node.calOutputPortPosNew(self.mFont)
                y += node_sizes[idx].height() + self.NODE_SPACING

            x_offset += layer_widths[layer_idx] + self.LAYER_SPACING

        for node_id in self.mGraph.nodes():
            node = self.mGraph.nodes[node_id]['node']
            node.calInputPortPos(self.mFont)

        canonical_pos = {}
        for node_id in self.mGraph.nodes():
            node = self.mGraph.nodes[node_id]['node']
            canonical_pos[node_id] = node.getNodePos()

        for node in self.mPipeline.getNodeList():
            node_id = self._node_key(node)
            if node_id in canonical_pos and node.getNodePos() is None:
                node.setNodePos(canonical_pos[node_id])

        Utils.LogD(self.TAG, ("%s: -" % (sys._getframe().f_code.co_name)))

    def order_ports(self):
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        for _ in range(3):
            for node_id in self.mGraph.nodes():
                node = self.mGraph.nodes[node_id]['node']
                self._order_output_ports(node)
            self._recalculate_port_positions()

            for node_id in self.mGraph.nodes():
                node = self.mGraph.nodes[node_id]['node']
                self._order_input_ports(node)
            self._recalculate_port_positions()
        Utils.LogD(self.TAG, ("%s: -" % (sys._getframe().f_code.co_name)))

    def _recalculate_port_positions(self):
        for node_id in self.mGraph.nodes():
            node = self.mGraph.nodes[node_id]['node']
            node.calPortPos()

    def _order_output_ports(self, node):
        output_ports = node.getOutputPort()
        if len(output_ports) <= 1:
            return

        port_barycenter = {}
        for port in output_ports:
            dst_ports = self.mPipeline.getPortLink().get(port, [])
            if dst_ports:
                y_positions = []
                for dp in dst_ports:
                    if dp.getPortPos() is not None and dp.getParentNodePos() is not None:
                        y_positions.append(dp.getParentNodePos().y() + dp.getPortPos().y())
                if y_positions:
                    port_barycenter[id(port)] = sum(y_positions) / len(y_positions)
                else:
                    port_barycenter[id(port)] = 0
            else:
                port_barycenter[id(port)] = 0

        node.mOutputPortList.sort(key=lambda p: port_barycenter.get(id(p), 0))

        child_map = {}
        for port in node.mOutputPortList:
            dst_ports = self.mPipeline.getPortLink().get(port, [])
            for dp in dst_ports:
                for child in self.mPipeline.getNodeList():
                    if self.mPipeline.matchNodePort(child, dp):
                        if child not in child_map:
                            child_map[child] = []
                        child_map[child].append(port)

        node.mChildNodeSortList = list(child_map.keys())
        node.mChildNodeToOutputPortMap = child_map

    def _order_input_ports(self, node):
        input_ports = node.getInputPort()
        if len(input_ports) <= 1:
            return

        port_barycenter = {}
        for port in input_ports:
            y_positions = []
            for src_port, dst_ports in self.mPipeline.getPortLink().items():
                for dp in dst_ports:
                    if dp.match(port) and src_port.getPortPos() is not None and src_port.getParentNodePos() is not None:
                        y_positions.append(src_port.getParentNodePos().y() + src_port.getPortPos().y())
            if y_positions:
                port_barycenter[id(port)] = sum(y_positions) / len(y_positions)
            else:
                port_barycenter[id(port)] = 0

        node.mInputPortList.sort(key=lambda p: port_barycenter.get(id(p), 0))
