# from collections import OrderedDict

import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui

from master_rigger.data import node_data


class Hierarchy(object):
    """
    Example Hiearchy:
    [
        'RigRootName', [
            'GLOBAL_MOVE', [
                'CTL',
                'IK',
                'JNT', [
                    'BONE',
                    'DRIVER'
                ]
            ]
        ]
    ]
    """

    defaultHierarchy = node_data.DEFAULT_RIG_HIERARCHY[:]

    def __init__(self, hierarchy, valueType='string'):
        self.hierarchy = hierarchy
        self.objectHierarchy = []

        if valueType == 'string':
            self.createHierarchy()
        elif valueType == 'object':
            self.createObjectHierarchy()

    def recurseBuild(self, contents, parentNode):
        latestNode = None
        for node in contents:
            if isinstance(node, str):
                latestNode = cmds.createNode('transform', name=node)
                if parentNode is not None:
                    cmds.parent(node, parentNode)
            elif isinstance(node, (list, tuple)):
                self.recurseBuild(node, latestNode)
            elif isinstance(node, dict):
                nodeTuples = node.items()
                for nodeTuple in nodeTuples:
                    self.recurseBuild(nodeTuple, latestNode)

    def recurseObjectBuild(self, contents, parentNode):
        latestNode = None
        row = []
        for node in contents:
            if isinstance(node, str):
                latestNode = TransformNode(name=node)
                if parentNode is not None:
                    latestNode._parent = parentNode
                row.append(latestNode)
            elif isinstance(node, (list, tuple)):
                children = self.recurseObjectBuild(node, latestNode)
                latestNode._children = children
        return row

    def createHierarchy(self):
        """
        Builds the hierarchy based on input

        - if self.hierarchy is a list type, recurseBuild will run normally
        - if self.hierarchy is a string, presume rig hierarchy and use input as the root node name
        - if self.hierarchy is a dict, runs similar to list but messier and does not maintain order

        """
        if isinstance(self.hierarchy, (list, tuple)):
            self.recurseBuild(self.hierarchy, None)
        elif isinstance(self.hierarchy, str):
            # Copy default rig hierarchy
            contents = self.defaultHierarchy
            contents[0] = self.hierarchy
            self.recurseBuild(contents, None)
        elif isinstance(self.hierarchy, dict):
            contents = self.hierarchy.items()
            self.recurseBuild(contents, None)

    def createObjectHierarchy(self):
        tree = self.recurseObjectBuild(self.hierarchy, None)
        self.objectHierarchy = tree


class TransformNode(object):

    def __init__(self, name='', parent=None):
        self._parent = parent
        self._name = name
        self._children = []

    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def insertChild(self, position, child):
        if 0 <= position < len(self._children):
            self._children.insert(position, child)
            child._parent = self
            return True
        return False

    def removeChild(self, position):
        if 0 <= position < len(self._children):
            child = self._children.pop(position)
            child._parent = None
            return True
        return False

    def getChildByIndex(self, index):
        if 0 <= index < len(self._children):
            return self._children[index]
        else:
            raise IndexError('Invalid index!')

    def getChildByName(self, name):
        for child in self._children:
            if child.name() == name:
                return child
        return None


class HierarchyTreeWidget(QtWidgets.QFrame):

    # Should have a dropdown of defaults/saved hierarchy builds
    defaultTree = Hierarchy(hierarchy=node_data.DEFAULT_RIG_HIERARCHY, valueType='object')

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        hierarchy_widget = QtWidgets.QWidget()
        hierarchy_widget.setLayout(QtWidgets.QVBoxLayout())
        hierarchy_widget.layout().setContentsMargins(2, 2, 2, 2)
        hierarchy_widget.layout().setSpacing(5)
        hierarchy_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(hierarchy_widget)

        tree_layout = QtWidgets.QHBoxLayout()

        hierarchy_widget.layout().addLayout(tree_layout)

        # ---------------
        self.treeData = {}

        # ---------------
        self.tree_widget = QtWidgets.QTreeView()
        model = QtGui.QStandardItemModel()
        self.tree_widget.setModel(model)
        self.rootItem = model.invisibleRootItem()

        self.addFromTree(self.defaultTree.objectHierarchy)
        tree_layout.addWidget(self.tree_widget)

        self.tree_widget.expandAll()

    def addItem(self, item, parent=''):
        tree_item = QtGui.QStandardItem(item.name())
        # tree_item.setData(item)
        if parent:
            parentItem = self.treeData[parent]
            parentItem.appendRow(tree_item)
        else:
            self.rootItem.appendRow(tree_item)
            self.treeData[item.name()] = tree_item

    def addChildrenFromTree(self, parent, children):
        for child in children:
            tree_item = QtGui.QStandardItem(child.name())
            parent.appendRow(tree_item)
            if child._children:
                self.addChildrenFromTree(tree_item, child._children)

    def addFromTree(self, tree):
        root = tree[0]
        tree_item = QtGui.QStandardItem(root.name())
        children = root._children

        self.rootItem.appendRow(tree_item)
        self.addChildrenFromTree(tree_item, children)
