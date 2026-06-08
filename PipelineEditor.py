import copy
import json

import json5
from PyQt5.Qt import QPoint

from Node import NodeDes
from Port import PortDes
from LayoutEngine import LayoutEngine


def _text(value):
    return "" if value is None else str(value)


class PipelineEditorCommand(object):
    def __init__(self, label, before_state, after_state):
        self.label = label
        self.before_state = before_state
        self.after_state = after_state


class PipelineEditController(object):
    TOOL_SELECT = "select"
    TOOL_ADD_NODE = "add_node"
    TOOL_LINK = "link"
    TOOL_DELETE = "delete"

    def __init__(self):
        self.pipeline = None
        self.json_path = None
        self.json_doc = None
        self.enabled = False
        self.dirty = False
        self.active_tool = self.TOOL_SELECT
        self.pending_src_port = None
        self.undo_stack = []
        self.redo_stack = []
        self.original_node_keys = set()
        self.created_node_keys = set()
        self.renamed_original_node_keys = {}

    def attach(self, pipeline, json_path):
        self.pipeline = pipeline
        self.json_path = json_path
        self.enabled = pipeline is not None and bool(json_path)
        self.dirty = False
        self.active_tool = self.TOOL_SELECT
        self.pending_src_port = None
        self.undo_stack = []
        self.redo_stack = []
        self.json_doc = None
        if self.enabled:
            with open(json_path, "r", encoding="utf-8") as fh:
                self.json_doc = json5.load(fh)
            self.original_node_keys = self._original_node_keys()

    def detach(self):
        self.__init__()

    def set_tool(self, tool):
        self.active_tool = tool
        if tool != self.TOOL_LINK:
            self.pending_src_port = None

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0

    def node_identity(self, node):
        return (_text(node.getNodeName()), _text(node.getNodeId()), _text(node.getNodeInstanceId()))

    def _original_node_keys(self):
        keys = set()
        node_entries = self._node_entries_from_doc(self.json_doc or {})
        for entry in node_entries:
            keys.add((_text(entry.get("NodeName")), _text(entry.get("NodeId")), _text(entry.get("NodeInstance"))))
        return keys

    def _node_entries_from_doc(self, doc):
        nodes = doc.get("Nodes", {}).get("Node", [])
        if isinstance(nodes, list):
            return nodes
        if isinstance(nodes, dict):
            return [nodes]
        return []

    def port_identity(self, port):
        return (_text(port.getNodeName()), _text(port.getNodeId()),
                _text(port.getNodeInstanceId()), _text(port.getPortId()), _text(port.getPortName()))

    def same_port(self, left, right):
        if left is None or right is None:
            return False
        return self.port_identity(left) == self.port_identity(right)

    def node_owns_port(self, node, port):
        if node is None or port is None:
            return False
        return (_text(node.getNodeName()), _text(node.getNodeId()), _text(node.getNodeInstanceId())) == (
            _text(port.getNodeName()), _text(port.getNodeId()), _text(port.getNodeInstanceId()))

    def node_has_rendered_port(self, node, port, output=None):
        if node is None or port is None:
            return False
        port_lists = []
        if output is None or output:
            port_lists.append(node.getOutputPort())
        if output is None or not output:
            port_lists.append(node.getInputPort())
        for ports in port_lists:
            for existing in ports:
                if existing is port or self.same_port(existing, port):
                    return True
        return False

    def node_uses_port(self, node, port, output=None):
        return self.node_owns_port(node, port) or self.node_has_rendered_port(node, port, output)

    def snapshot(self):
        if self.pipeline is None:
            return None
        nodes = []
        for node in self.pipeline.getNodeList():
            nodes.append({
                "name": _text(node.getNodeName()),
                "id": _text(node.getNodeId()),
                "instance": _text(node.getNodeInstance()),
                "instance_id": _text(node.getNodeInstanceId()),
                "target_name": _text(node.getTargetName()),
                "target_node": bool(node.isTargetNode()),
                "source_node": bool(node.isSourceNode()),
                "props": [tuple(prop) for prop in node.getNodeProp()],
                "inputs": [self._port_snapshot(port) for port in node.getInputPort()],
                "outputs": [self._port_snapshot(port) for port in node.getOutputPort()],
                "pos": self._point_snapshot(node.getNodePos()),
                "size": self._size_snapshot(node.getNodeSize()),
                "font": node.getNodeFontSize()
            })

        links = []
        for src_port, dst_ports in self.pipeline.getPortLink().items():
            for dst_port in dst_ports:
                links.append({
                    "src": self._port_snapshot(src_port),
                    "dst": self._port_snapshot(dst_port)
                })
        return {
            "pipeline_name": self.pipeline.getPipelineName(),
            "pipeline_keys": copy.deepcopy(self.pipeline.getPipelineKeys()),
            "nodes": nodes,
            "links": links
        }

    def _point_snapshot(self, point):
        if point is None:
            return None
        return [int(point.x()), int(point.y())]

    def _size_snapshot(self, size):
        if size is None:
            return None
        return [int(size.width()), int(size.height())]

    def _port_snapshot(self, port):
        return {
            "name": _text(port.getPortName()),
            "id": _text(port.getPortId()),
            "node_name": _text(port.getNodeName()),
            "node_id": _text(port.getNodeId()),
            "node_instance": _text(port.getNodeInstance()),
            "node_instance_id": _text(port.getNodeInstanceId()),
            "target": bool(port.isTargetPort())
        }

    def restore(self, state):
        if self.pipeline is None or state is None:
            return
        self.pipeline.mNodeList = []
        self.pipeline.mPortLinkDes = {}
        self.pipeline.mInputPortList = []
        self.pipeline.mSrcNodeList = []
        self.pipeline.mNodeLevelKeyMap = {}
        self.pipeline.mNodeLevelKeyList = []
        self.pipeline.mMaxLevel = 0
        self.pipeline.setPipelineName(state.get("pipeline_name", ""))
        self.pipeline.setPipelineKeys(copy.deepcopy(state.get("pipeline_keys", {})))

        node_map = {}
        for node_state in state.get("nodes", []):
            node = NodeDes(node_state["name"], node_state["id"], node_state["instance"],
                           node_state["instance_id"], node_state.get("target_name", ""))
            node.setTargetNode(node_state.get("target_node", False))
            node.setSourceNodeFlag(node_state.get("source_node", False))
            for prop in node_state.get("props", []):
                values = list(prop) + [None, None, None, None]
                node.setNodePorp(values[0], values[1], values[2], values[3])
            for port_state in node_state.get("inputs", []):
                node.addInputPort(self._port_from_state(port_state))
            for port_state in node_state.get("outputs", []):
                node.addOutputPort(self._port_from_state(port_state))
            pos = node_state.get("pos")
            if pos is not None:
                node.setNodePos(QPoint(pos[0], pos[1]))
            font_size = node_state.get("font") or 24
            node.setNodeFont(font_size)
            size = node_state.get("size")
            if size is not None:
                from PyQt5.Qt import QSize
                node.setNodeSize(QSize(size[0], size[1]))
            else:
                node.calNodeSize()
            node.calPortPos()
            self.pipeline.mNodeList.append(node)
            node_map[self.node_identity(node)] = node

        for link_state in state.get("links", []):
            src = self._canonical_port(link_state["src"], True, node_map)
            dst = self._canonical_port(link_state["dst"], False, node_map)
            self._append_link(src, dst)

    def _port_from_state(self, state):
        port = PortDes(state["name"], state["id"], state["node_name"], state["node_id"],
                       state["node_instance"], state["node_instance_id"])
        port.setTargetPort(state.get("target", False))
        return port

    def _canonical_port(self, port_state, output, node_map=None):
        port = self._port_from_state(port_state)
        if node_map is None:
            node_map = {self.node_identity(node): node for node in self.pipeline.getNodeList()}

        # Keep links attached to the same rendered port object captured in the
        # snapshot. Some legacy JSON pipelines display a port on a node matched
        # by NodeId/NodeInstance even when the port's NodeName differs.
        for node in node_map.values():
            ports = node.getOutputPort() if output else node.getInputPort()
            for existing in ports:
                if self.same_port(existing, port):
                    return existing

        node_key = (_text(port.getNodeName()), _text(port.getNodeId()), _text(port.getNodeInstanceId()))
        node = node_map.get(node_key)
        if node is None:
            return port
        ports = node.getOutputPort() if output else node.getInputPort()
        for existing in ports:
            if _text(existing.getPortId()) == _text(port.getPortId()) and _text(existing.getPortName()) == _text(port.getPortName()):
                return existing
        ports.append(port)
        node.calNodeSize()
        node.calPortPos()
        return port

    def _append_link(self, src_port, dst_port):
        for existing_src, dst_ports in list(self.pipeline.mPortLinkDes.items()):
            if self.same_port(existing_src, src_port):
                if not any(self.same_port(port, dst_port) for port in dst_ports):
                    dst_ports.append(dst_port)
                return
        self.pipeline.mPortLinkDes[src_port] = [dst_port]

    def commit(self, label, before_state):
        after_state = self.snapshot()
        if before_state == after_state:
            return False
        self.undo_stack.append(PipelineEditorCommand(label, before_state, after_state))
        self.redo_stack = []
        self.dirty = True
        return True

    def undo(self):
        if not self.can_undo():
            return None
        command = self.undo_stack.pop()
        self.restore(command.before_state)
        self.redo_stack.append(command)
        self.dirty = True
        return command.label

    def redo(self):
        if not self.can_redo():
            return None
        command = self.redo_stack.pop()
        self.restore(command.after_state)
        self.undo_stack.append(command)
        self.dirty = True
        return command.label

    def duplicate_node(self, template_node, fields, pos):
        before = self.snapshot()
        node = NodeDes(fields["NodeName"], fields["NodeId"], fields["NodeInstance"],
                       fields["NodeInstanceId"], template_node.getTargetName())
        node.setTargetNode(template_node.isTargetNode())
        for prop in template_node.getNodeProp():
            values = list(prop) + [None, None, None, None]
            node.setNodePorp(values[0], values[1], values[2], values[3])
        for name, port_id in fields.get("InputPorts", []):
            node.addInputPort(PortDes(name, port_id, fields["NodeName"], fields["NodeId"],
                                      fields["NodeInstance"], fields["NodeInstanceId"]))
        for name, port_id in fields.get("OutputPorts", []):
            node.addOutputPort(PortDes(name, port_id, fields["NodeName"], fields["NodeId"],
                                       fields["NodeInstance"], fields["NodeInstanceId"]))
        if pos is not None:
            node.setNodePos(QPoint(pos))
        else:
            node.setNodePos(QPoint(260, 180))
        node.setNodeFont(template_node.getNodeFontSize() or 24)
        node.calNodeSize()
        node.calPortPos()
        self.pipeline.addNode(node)
        self.created_node_keys.add(self.node_identity(node))
        self.commit("Add node", before)
        return node

    def update_node_fields(self, node, fields):
        before = self.snapshot()
        old_key = self.node_identity(node)
        node.mNodeName = fields["NodeName"]
        node.mNodeId = fields["NodeId"]
        node.mNodeInstance = fields["NodeInstance"]
        node.mNodeInstanceId = fields["NodeInstanceId"]
        node.mInputPortList = []
        node.mOutputPortList = []
        for name, port_id in fields.get("InputPorts", []):
            node.addInputPort(PortDes(name, port_id, node.getNodeName(), node.getNodeId(),
                                      node.getNodeInstance(), node.getNodeInstanceId()))
        for name, port_id in fields.get("OutputPorts", []):
            node.addOutputPort(PortDes(name, port_id, node.getNodeName(), node.getNodeId(),
                                       node.getNodeInstance(), node.getNodeInstanceId()))
        self._retarget_links(old_key, node)
        node.calNodeSize()
        node.calPortPos()
        new_key = self.node_identity(node)
        if old_key in self.created_node_keys:
            self.created_node_keys.discard(old_key)
            self.created_node_keys.add(new_key)
        if old_key in self.original_node_keys or old_key in self.renamed_original_node_keys:
            root_key = self.renamed_original_node_keys.pop(old_key, old_key)
            self.renamed_original_node_keys[new_key] = root_key
        self.commit("Edit node", before)

    def _retarget_links(self, old_key, node):
        new_links = {}
        for src, dst_ports in self.pipeline.mPortLinkDes.items():
            src = self._retarget_port(src, old_key, node, True)
            new_dst_ports = [self._retarget_port(dst, old_key, node, False) for dst in dst_ports]
            new_links[src] = new_dst_ports
        self.pipeline.mPortLinkDes = new_links

    def _retarget_port(self, port, old_key, node, output):
        port_key = (_text(port.getNodeName()), _text(port.getNodeId()), _text(port.getNodeInstanceId()))
        if port_key != old_key:
            return port
        ports = node.getOutputPort() if output else node.getInputPort()
        if len(ports) > 0:
            return ports[0]
        return PortDes("port_0", "0", node.getNodeName(), node.getNodeId(),
                       node.getNodeInstance(), node.getNodeInstanceId())

    def delete_node(self, node):
        before = self.snapshot()
        self.pipeline.mNodeList = [item for item in self.pipeline.getNodeList() if item is not node]
        new_links = {}
        for src, dst_ports in self.pipeline.mPortLinkDes.items():
            if self.node_uses_port(node, src, True):
                continue
            kept = [dst for dst in dst_ports if not self.node_uses_port(node, dst, False)]
            if kept:
                new_links[src] = kept
        self.pipeline.mPortLinkDes = new_links
        self.commit("Delete node", before)

    def add_link(self, src_port, dst_port):
        before = self.snapshot()
        self._append_link(src_port, dst_port)
        self.commit("Add link", before)

    def delete_link(self, src_port, dst_port):
        before = self.snapshot()
        for src, dst_ports in list(self.pipeline.mPortLinkDes.items()):
            if src is src_port or self.same_port(src, src_port):
                self.pipeline.mPortLinkDes[src] = [
                    dst for dst in dst_ports
                    if not (dst is dst_port or self.same_port(dst, dst_port))
                ]
                if len(self.pipeline.mPortLinkDes[src]) == 0:
                    self.pipeline.mPortLinkDes.pop(src, None)
                break
        self.commit("Delete link", before)

    def relayout(self, point, font_size):
        before = self.snapshot()
        for node in self.pipeline.getNodeList():
            node.mNodeLevelList = []
            node.mNodeLevelSet = set()
            node.mChildNodeToOutputPortMap = {}
            node.mParentNodeToInputPortMap = {}
            node.mChildNodeSortList = []
            node.mParentNodeList = []
        layout_engine = LayoutEngine(self.pipeline)
        layout_engine.compute_layout(point, font_size)
        self.commit("Re-layout", before)

    def validate(self):
        errors = []
        identities = {}
        for node in self.pipeline.getNodeList():
            key = self.node_identity(node)
            if not key[0] or not key[1] or not key[2]:
                errors.append("Node identity fields cannot be empty.")
            if key in identities:
                errors.append("Duplicate node identity: %s_%s_%s" % key)
            identities[key] = node
            self._validate_ports(node.getInputPort(), node, "input", errors)
            self._validate_ports(node.getOutputPort(), node, "output", errors)

        for src, dst_ports in self.pipeline.getPortLink().items():
            if self.find_node_for_port(src) is None:
                errors.append("Link source has no node: %s_%s" % (src.getNodeName(), src.getPortId()))
            for dst in dst_ports:
                if self.find_node_for_port(dst) is None:
                    errors.append("Link destination has no node: %s_%s" % (dst.getNodeName(), dst.getPortId()))
        return errors

    def _validate_ports(self, ports, node, label, errors):
        seen = set()
        for port in ports:
            key = (_text(port.getPortName()), _text(port.getPortId()))
            if not key[0] or not key[1]:
                errors.append("%s port on %s has empty fields." % (label, node.getNodeName()))
            if key in seen:
                errors.append("Duplicate %s port on %s: %s_%s" % (label, node.getNodeName(), key[0], key[1]))
            seen.add(key)

    def find_node_for_port(self, port):
        for node in self.pipeline.getNodeList():
            if self.pipeline.matchNodePort(node, port):
                return node
        return None

    def save_json(self):
        errors = self.validate()
        if errors:
            return False, "\n".join(errors[:12])
        doc = self.build_json_doc()
        with open(self.json_path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(self.json_path, "r", encoding="utf-8") as fh:
            json5.load(fh)
        self.dirty = False
        return True, self.json_path

    def build_json_doc(self):
        doc = copy.deepcopy(self.json_doc or {})
        doc["PipelineName"] = self.pipeline.getPipelineName()
        if self.pipeline.getPipelineKeys():
            doc["PipelineKeys"] = copy.deepcopy(self.pipeline.getPipelineKeys())
        doc["Nodes"] = {"Node": self._json_nodes()}
        doc["PortLinks"] = {"Link": self._json_links()}
        return doc

    def _json_nodes(self):
        result = []
        for node in self.pipeline.getNodeList():
            key = self.node_identity(node)
            if key not in self.original_node_keys and key not in self.created_node_keys and key not in self.renamed_original_node_keys:
                continue
            props = []
            for prop in node.getNodeProp():
                entry = {}
                if len(prop) > 1 and prop[1] not in (None, "None"):
                    entry["Id"] = self._json_scalar(prop[1])
                if len(prop) > 3 and prop[3] not in (None, "None"):
                    entry["Value"] = prop[3]
                props.append(entry)
            result.append({
                "NodeName": node.getNodeName(),
                "NodeInstance": self._json_scalar(node.getNodeInstance()),
                "NodeId": self._json_scalar(node.getNodeId()),
                "NodeProperties": props
            })
        return result

    def _json_links(self):
        links = []
        original_links = self._original_link_map()
        for src, dst_ports in self.pipeline.getPortLink().items():
            for dst in dst_ports:
                key = (self._port_key(src), self._port_key(dst))
                link = copy.deepcopy(original_links.get(key, {}))
                link["SrcPort"] = self._json_port(src, link.get("SrcPort", {}))
                link["DstPort"] = self._json_port(dst, link.get("DstPort", {}))
                links.append({
                    key: value for key, value in link.items()
                })
        return links

    def _original_link_map(self):
        result = {}
        links = self.json_doc.get("PortLinks", {}).get("Link", []) if self.json_doc else []
        if isinstance(links, dict):
            links = [links]
        for link in links:
            src = link.get("SrcPort", {})
            dst = link.get("DstPort", {})
            result[(self._json_port_key(src), self._json_port_key(dst))] = link
        return result

    def _json_port_key(self, port):
        return (_text(port.get("NodeName")), _text(port.get("NodeId")),
                _text(port.get("NodeInstance")), _text(port.get("PortId")))

    def _port_key(self, port):
        return (_text(port.getNodeName()), _text(port.getNodeId()),
                _text(port.getNodeInstance()), _text(port.getPortId()))

    def _json_port(self, port, original=None):
        data = copy.deepcopy(original or {})
        data.update({
            "PortId": self._json_scalar(port.getPortId()),
            "NodeInstance": self._json_scalar(port.getNodeInstance()),
            "NodeName": port.getNodeName(),
            "NodeId": self._json_scalar(port.getNodeId())
        })
        return data

    def _json_scalar(self, value):
        try:
            text = str(value)
            if text.strip() == "":
                return text
            if text == str(int(text)):
                return int(text)
        except Exception:
            pass
        return value
