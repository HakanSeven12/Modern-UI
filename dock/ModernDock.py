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

mw = FreeCADGui.getMainWindow()

class ModernDock(QtCore.QObject):
    side = False
    docked = True
    target = None
    autoHide = 1

    def __init__(self, dock):
        super(ModernDock, self).__init__(dock)
        self.setObjectName(dock.objectName()+"minMax")
        mw.mainWindowClosed.connect(self.onClose)
        dock.installEventFilter(self)
        area = mw.dockWidgetArea(dock)

        btnSize = QtCore.QSize(16, 16)
        title = QtWidgets.QLabel(dock.windowTitle())
        closeBtn = QtWidgets.QToolButton()
        icon = dock.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton)
        closeBtn.setIcon( icon )
        closeBtn.setFixedSize(btnSize)
        closeBtn.clicked.connect(self.pin)
        minimizeBtn = QtWidgets.QToolButton()
        icon = dock.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMinButton)
        minimizeBtn.setIcon( icon )
        minimizeBtn.setFixedSize(btnSize)
        minimizeBtn.clicked.connect(self.minMax)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(minimizeBtn)
        layout.addWidget(closeBtn)
        title_bar = QtWidgets.QWidget()
        title_bar.setLayout(layout)
        dock.setTitleBarWidget(title_bar)

        self.visible = dock.features()
        self.orgHeight = dock.sizeHint().height()
        self.orgWidth = dock.sizeHint().width()
        self.collapsedDock(dock, area)
        self.target = dock

    def pin(self):
        self.target.hide()

    def minMax(self):
        area = mw.dockWidgetArea(self.target)

        if self.autoHide:
            for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                    object = mw.findChildren(QtCore.QObject, dockWid.objectName()+"minMax")
                    self.openDock(dockWid)
                    dockWid.removeEventFilter(object[0])
        else:
            for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                    object = mw.findChildren(QtCore.QObject, dockWid.objectName()+"minMax")
                    self.collapsedDock(dockWid, area)
                    dockWid.installEventFilter(object[0])
        self.autoHide = (self.autoHide + 1) % 2

    def eventFilter(self, source, event):
        area = mw.dockWidgetArea(self.target)
        if source is self.target:
            if (event.type() is event.Enter) or \
                (self.target.isFloating() and self.docked):
                for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                    if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                        self.openDock(dockWid)
                return True

            elif event.type() is event.Leave:
                for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                    if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                        self.collapsedDock(dockWid, area)
                return True

        return super(ModernDock, self).eventFilter(source, event)

    def openDock(self, dock):
        dock.setMaximumSize(5000, 5000)
        dock.setFeatures(self.visible)
        self.docked = False
        self.modifyDock(dock, self.orgWidth, self.orgHeight)


    def collapsedDock(self, dock, area):
        self.side = False
        self.docked = True
        dock.setMaximumSize(5000, 5000)

        if (area is QtCore.Qt.LeftDockWidgetArea) or \
            (area is QtCore.Qt.RightDockWidgetArea):
            self.side = True
            features = QtWidgets.QDockWidget.DockWidgetFeatures(
                self.visible | QtWidgets.QDockWidget.DockWidgetVerticalTitleBar)
            dock.setFeatures(features)
        TBHeight = 25
        # Segmantation fault
        #TBHeight = dock.style().pixelMetric(
        #       QtWidgets.QStyle.PM_TitleBarHeight)
        self.modifyDock(dock, TBHeight, TBHeight)

    def modifyDock(self, dock, width, height):
        if self.side:
            dock.setFixedWidth(width)
        else:
            dock.setFixedHeight(height)
        dock.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def onClose(self):
        self.deleteLater()

def run():
    for dock in mw.findChildren(QtWidgets.QDockWidget):
        ModernDock(dock)
