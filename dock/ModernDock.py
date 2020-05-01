# ***********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 3 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

"""
This class makes by hides the FreeCAD docks (sidebars), by default. 
When the mouse moves towards them, they become visible.
"""

import FreeCADGui
from PySide2 import QtCore, QtGui, QtWidgets
from menu.common import createButton
import os

path = os.path.dirname(__file__) + "/../Resources/icons/"
mw = FreeCADGui.getMainWindow()

class ModernDock(QtCore.QObject):
    side = False
    docked = True
    target = None
    autoHide = 1
    title = None
    minimizeBtn = None

    def __init__(self, dock):
        super(ModernDock, self).__init__(dock)
        self.setObjectName(dock.objectName()+"pin")
        mw.mainWindowClosed.connect(self.onClose)
        dock.topLevelChanged.connect(self.onChange)
        if dock.windowTitle().replace('&', '') == "Combo View":
            tab = dock.findChildren(QtWidgets.QTabWidget,"combiTab")[0]
            tab.currentChanged.connect(self.pin)

        dock.installEventFilter(self)
        mw.installEventFilter(self)
        area = mw.dockWidgetArea(dock)
        self.visible = dock.features()
        self.redesignTitlebar(dock)

        self.orgHeight = dock.sizeHint().height()
        self.orgWidth = dock.sizeHint().width()
        self.collapsedDock(dock, area)

    def redesignTitlebar(self, dock):
        btnSize = QtCore.QSize(16, 16)
        title = QtWidgets.QLabel(dock.windowTitle())
        closeBtn = QtWidgets.QToolButton()
        closeBtn.setFixedSize(btnSize)
        Icon = QtGui.QIcon(path+'Hide')
        closeBtn.setIcon(Icon)
        closeBtn.setIconSize(btnSize)
        closeBtn.clicked.connect(self.hide)
        minimizeBtn = QtWidgets.QToolButton()
        Icon = QtGui.QIcon(path+'Pin')
        minimizeBtn.setIcon(Icon)
        minimizeBtn.setFixedSize(btnSize)
        minimizeBtn.clicked.connect(self.pin)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(minimizeBtn)
        layout.addWidget(closeBtn)
        title_bar = QtWidgets.QWidget()
        title_bar.setLayout(layout)
        dock.setTitleBarWidget(title_bar)

        self.minimizeBtn = minimizeBtn
        self.target = dock
        self.title = title

    def pin(self):
        area = mw.dockWidgetArea(self.target)

        for dockWid in mw.findChildren(QtWidgets.QDockWidget):
            if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                if self.autoHide or dockWid.isFloating():
                    self.disableCollapsing(dockWid)
                else:
                    self.enableCollapsing(dockWid)
        self.autoHide = (self.autoHide + 1) % 2
    
    def onChange(self):
        if self.autoHide and self.target.isFloating():
            self.disableCollapsing(self.target)
        else:
            self.enableCollapsing(self.target)

    def disableCollapsing(self, dock):
        object = mw.findChildren(QtCore.QObject, dock.objectName()+"pin")[0]
        Icon = QtGui.QIcon(path+'UnPin')
        object.minimizeBtn.setIcon(Icon)
        self.openDock(dock)
        dock.setMinimumSize(0, 0)
        dock.setMaximumSize(5000, 5000)
        try: dock.removeEventFilter(object)
        except Exception: pass
        
    def enableCollapsing(self, dock):
        object = mw.findChildren(QtCore.QObject, dock.objectName()+"pin")[0]
        Icon = QtGui.QIcon(path+'Pin')
        object.minimizeBtn.setIcon(Icon)
        self.orgHeight = dock.size().height()
        self.orgWidth = dock.size().width()
        try: dock.installEventFilter(object)
        except Exception: pass

    def eventFilter(self, source, event):
        area = mw.dockWidgetArea(self.target)

        if source is mw and event.type() is event.ChildAdded:
            if isinstance(event.child(), QtWidgets.QDockWidget):
                for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                    if dockWid.windowTitle().replace('&', '') == "Modern Menu":continue
                    object = mw.findChildren(QtCore.QObject, dockWid.objectName()+"pin")
                    if not object: ModernDock(dockWid)
            return True

        elif source is self.target:
            if (event.type() is event.Enter) or \
                (self.target.isFloating() and self.docked):
                for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                    if dockWid.windowTitle().replace('&', '') == "Modern Menu":continue
                    if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                        if dockWid.isFloating() == False:
                            self.openDock(dockWid)
                return True

            elif event.type() is event.Leave:
                for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                    if dockWid.windowTitle().replace('&', '') == "Modern Menu": continue
                    if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                        if dockWid.isFloating() == False:
                            self.collapsedDock(dockWid, area)
                return True
        """
        elif event.type() is QtCore.QEvent.User:
            report = mw.findChildren(QtWidgets.QDockWidget, "Report view")[0]
            msgType = event.messageType()
            if msgType == ReportHighlighter.Error or msgType == ReportHighlighter.Warning:
                self.openDock(report)
            return True
        """
        return super(ModernDock, self).eventFilter(source, event)

    def openDock(self, dock):
        dock.setFeatures(self.visible)
        object = mw.findChildren(QtCore.QObject, dock.objectName()+"pin")[0]
        title = dock.windowTitle().replace('&', '')
        object.title.setText(title)
        self.docked = False
        self.modifyDock(dock, self.orgWidth, self.orgHeight)

    def collapsedDock(self, dock, area):
        self.side = False
        self.docked = True
        TBHeight = 24

        if (area is QtCore.Qt.LeftDockWidgetArea) or \
            (area is QtCore.Qt.RightDockWidgetArea):
            self.side = True
            object = mw.findChildren(QtCore.QObject, dock.objectName()+"pin")[0]
            text = dock.windowTitle().replace('&', '')
            title = "\n".join(text) + " "
            object.title.setText(title)
            features = QtWidgets.QDockWidget.DockWidgetFeatures(
                self.visible | QtWidgets.QDockWidget.DockWidgetVerticalTitleBar)
            dock.setFeatures(features)
        self.modifyDock(dock, TBHeight, TBHeight)

    def modifyDock(self, dock, width, height):
        if self.side:
            dock.setMinimumWidth(width-1)
            dock.setMaximumWidth(width)
            dock.setMinimumHeight(0)
            dock.setMaximumHeight(5000)
        else:
            dock.setMinimumHeight(height-1)
            dock.setMaximumHeight(height)
            dock.setMinimumWidth(0)
            dock.setMaximumWidth(5000)

    def hide(self):
        self.target.hide()

    def onClose(self):
        self.deleteLater()

def run():
    for dock in mw.findChildren(QtWidgets.QDockWidget):
        #if dock.windowTitle() == "Report view":continue
        if dock.windowTitle().replace('&', '') == "Modern Menu":continue
        ModernDock(dock)
