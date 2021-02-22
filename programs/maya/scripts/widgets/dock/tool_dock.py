from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm
from maya import cmds
from functools import partial
# check these on home setup as well, might be out of date
try:
    # Maya 2017+
    from shiboken2 import wrapInstance
except ImportError:
    # Maya 2016-
    from shiboken import wrapInstance
from maya import OpenMayaUI as omui

# Dockable options
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget

from master_rigger import Splitter
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node
from master_rigger import basicTools as tool
from master_rigger import basicRigSetup as rig
from master_rigger import curve_assignment as crv
from master_rigger import renamerLibrary as name
from master_rigger import riggingTools as rTool
from master_rigger import hierarchy
from dockTools import skeletonWidgets as skele
from dockTools import globalWidget as glob
reload(attr)
reload(node)
reload(tool)
reload(rig)
reload(crv)
reload(name)
reload(skele)
reload(rTool)
reload(glob)
reload(hierarchy)


class RiggingDock(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    window_name = 'Rigging Dock'

    def __init__(self, parent=None, ss_path=''):  # set default ss if made
        super(RiggingDock, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(self.window_name)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Temp forced resizers, remove later and set default sizes
        # self.setFixedHeight(400)
        # self.setFixedWidth(600)

        # Optional Stylesheet for later work
        try:
            style_sheet_file = open(ss_path)
            self.setStyleSheet(style_sheet_file.read())
        except IOError:
            pass

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)

        text_layout = QtWidgets.QHBoxLayout()
        text_layout.setSpacing(5)
        self.layout().addLayout(text_layout)

        # Temporary placeholders to keep the dock active
        example_label = QtWidgets.QLabel('Title:')
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        example_label.setFont(bold_font)

        example_line_edit = QtWidgets.QLineEdit()
        example_line_edit.setPlaceholderText('')

        text_layout.addWidget(example_label)
        text_layout.addWidget(example_line_edit)

        self.layout().addWidget(Splitter.Splitter('Global Tools'))

        global_tools_layout = QtWidgets.QHBoxLayout()
        global_tools_layout.setSpacing(5)
        self.layout().addLayout(global_tools_layout)

        global_tools_widget = glob.GlobalToolWidget()
        global_tools_layout.addWidget(global_tools_widget)
        self.layout().addLayout(Splitter.SplitterLayout())

        # Tabs Layout ----------------------------------------------------------
        tab_layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(tab_layout)

        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setTabPosition(tab_widget.West)
        tab_layout.addWidget(tab_widget)

        # Rigging categories
        general_tools_layout = QtWidgets.QVBoxLayout()
        skeleton_tools_layout = QtWidgets.QVBoxLayout()
        deformer_tools_layout = QtWidgets.QVBoxLayout()
        skinning_tools_layout = QtWidgets.QVBoxLayout()
        control_tools_layout = QtWidgets.QVBoxLayout()
        viewport_tools_layout = QtWidgets.QVBoxLayout()
        custom_tools_layout = QtWidgets.QVBoxLayout()

        # General tools tab ----------------------------------------------------
        general_tab = QtWidgets.QWidget()
        tab_widget.addTab(general_tab, 'General')
        general_tab.setLayout(general_tools_layout)

        # Naming functions
        name_ui = name.NamingWidget()
        general_tools_layout.addWidget(name_ui)
        general_tab.layout().addLayout(Splitter.SplitterLayout())

        # Attribute functions
        general_tab.layout().addWidget(Splitter.Splitter('Edit Attribute'))
        attr_ui = attr.AttributeWidget()
        general_tools_layout.addWidget(attr_ui)
        general_tab.layout().addLayout(Splitter.SplitterLayout())

        general_tab.layout().addWidget(Splitter.Splitter('Create Attribute'))
        add_attr_ui = attr.AddAttributesWidget()
        general_tools_layout.addWidget(add_attr_ui)
        general_tab.layout().addLayout(Splitter.SplitterLayout())

        # Node functions
        general_tab.layout().addWidget(Splitter.Splitter('Nodes'))
        node_ui = node.NodeWidget()
        general_tools_layout.addWidget(node_ui)
        general_tab.layout().addLayout(Splitter.SplitterLayout())

        # Dead Space Killer
        general_tab.layout().addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        )

        # Skeleton tools tab ---------------------------------------------------
        # skeleton_tab = QtWidgets.QWidget()
        # tab_widget.addTab(skeleton_tab, 'Skeleton')
        # skeleton_tab.setLayout(skeleton_tools_layout)

        # skeleton_tab.layout().addWidget(Splitter.Splitter('Skeleton Tools'))
        # skeleton_ui = skele.SkeletonToolsWidget()
        # skeleton_tools_layout.addWidget(skeleton_ui)
        # skeleton_tab.layout().addLayout(Splitter.SplitterLayout())

        # # Dead Space Killer
        # skeleton_tab.layout().addSpacerItem(
        #     QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
        #                           QtWidgets.QSizePolicy.Expanding)
        # )

        # Deformer tools tab ---------------------------------------------------
        # deformer_tab = QtWidgets.QWidget()
        # tab_widget.addTab(deformer_tab, 'Deformers')
        # deformer_tab.setLayout(deformer_tools_layout)

        # Skinning tools tab ---------------------------------------------------
        # skinning_tab = QtWidgets.QWidget()
        # tab_widget.addTab(skinning_tab, 'Skinning')
        # skinning_tab.setLayout(skinning_tools_layout)

        # Control tools tab ----------------------------------------------------
        controls_tab = QtWidgets.QWidget()
        tab_widget.addTab(controls_tab, 'Controls')
        controls_tab.setLayout(control_tools_layout)

        # Create Controls functions
        controls_tab.layout().addWidget(Splitter.Splitter('Create Controls'))
        curve_ui = crv.ControlCurveWidget()
        control_tools_layout.addWidget(curve_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Offset functions
        controls_tab.layout().addWidget(Splitter.Splitter('Offsets'))
        offset_ui = tool.OffsetNodeWidget()
        control_tools_layout.addWidget(offset_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Match transformations
        controls_tab.layout().addWidget(Splitter.Splitter('Transformations'))
        transforms_ui = tool.TransformWidget()
        control_tools_layout.addWidget(transforms_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Create Rig
        controls_tab.layout().addWidget(Splitter.Splitter('Create Rig'))
        rig_ui = rig.CreateRigWidget()
        control_tools_layout.addWidget(rig_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Constraints
        controls_tab.layout().addWidget(Splitter.Splitter('Constraints'))
        constraints_ui = rTool.ConstraintWidget()
        control_tools_layout.addWidget(constraints_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Hierarchy
        controls_tab.layout().addWidget(Splitter.Splitter('Hierarchy Tree'))
        hierarchy_ui = hierarchy.HierarchyTreeWidget()
        control_tools_layout.addWidget(hierarchy_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Vector Aim Constraint
        # controls_tab.layout().addWidget(Splitter.Splitter('Vector Aim Constraint (WIP)'))
        # aim_ui = rTool.VectorWidget()
        # control_tools_layout.addWidget(aim_ui)
        # controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Rivets (Move Later)
        controls_tab.layout().addWidget(Splitter.Splitter('Rivet (WIP)'))
        rivet_ui = rTool.RivetWidget()
        control_tools_layout.addWidget(rivet_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # PV Solver (Move Later)
        controls_tab.layout().addWidget(Splitter.Splitter('Pole Vector Solver (WIP)'))
        pv_ui = rTool.PVWidget()
        control_tools_layout.addWidget(pv_ui)
        controls_tab.layout().addLayout(Splitter.SplitterLayout())

        # Dead Space Killer
        controls_tab.layout().addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        )

        # Viewport tools tab ---------------------------------------------------
        viewport_tab = QtWidgets.QWidget()
        tab_widget.addTab(viewport_tab, 'Viewport')
        viewport_tab.setLayout(viewport_tools_layout)

        # Isolate Selection functions (move later?)
        viewport_tab.layout().addWidget(Splitter.Splitter('Isolate Options'))
        isolate_ui = tool.IsolateSelectionWidget()
        viewport_tools_layout.addWidget(isolate_ui)
        viewport_tab.layout().addLayout(Splitter.SplitterLayout())

        # Dead Space Killer
        viewport_tools_layout.layout().addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        )

        # Custom tools tab -----------------------------------------------------
        custom_tab = QtWidgets.QWidget()
        tab_widget.addTab(custom_tab, 'Custom')
        custom_tab.setLayout(custom_tools_layout)

    # Review widget delete/closing at a later time
    def dockCloseEventTriggered(self):
        self.deleteInstances()

    def deleteInstances(self):
        dialog.deleteLater()


dialog = None


def show_ui(docked=True):
    global dialog
    if dialog is None:
        dialog = RiggingDock()
    if docked:
        dialog.show(dockable=True, floating=False, area='right')
    else:
        dialog.show()
