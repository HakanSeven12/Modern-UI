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

    def __init__(self, dock):
        super(ModernDock, self).__init__(dock)
        self.setObjectName(dock.objectName()+"minMax")
        mw.mainWindowClosed.connect(self.onClose)
        self.orgTitle = dock.titleBarWidget()
        dock.installEventFilter(self)
        area = mw.dockWidgetArea(dock)
        self.visible = dock.features()

        btnSize = QtCore.QSize(16, 16)
        title = QtWidgets.QLabel(dock.windowTitle())
        closeBtn = QtWidgets.QToolButton()
        closeBtn.setFixedSize(btnSize)
        Icon = QtGui.QIcon(path+'Hide')
        closeBtn.setIcon(Icon)
        closeBtn.setIconSize(btnSize)
        closeBtn.clicked.connect(self.pin)
        minimizeBtn = QtWidgets.QToolButton()
        Icon = QtGui.QIcon(path+'Pin')
        minimizeBtn.setIcon(Icon)
        minimizeBtn.setFixedSize(btnSize)
        minimizeBtn.clicked.connect(self.minMax)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(minimizeBtn)
        layout.addWidget(closeBtn)
        title_bar = QtWidgets.QWidget()
        title_bar.setLayout(layout)
        dock.setTitleBarWidget(title_bar)

        self.orgHeight = dock.sizeHint().height()
        self.orgWidth = dock.sizeHint().width()
        self.target = dock
        self.title = title
        self.minimizeBtn = minimizeBtn
        self.collapsedDock(dock, area)

    def pin(self):
        self.target.hide()

    def minMax(self):
        area = mw.dockWidgetArea(self.target)

        if self.autoHide:
            for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                    object = mw.findChildren(QtCore.QObject, dockWid.objectName()+"minMax")
                    Icon = QtGui.QIcon(path+'UnPin')
                    self.minimizeBtn.setIcon(Icon)
                    self.openDock(dockWid)
                    dockWid.setMinimumSize(0, 0)
                    dockWid.setMaximumSize(5000, 5000)
                    dockWid.removeEventFilter(object[0])
        else:
            for dockWid in mw.findChildren(QtWidgets.QDockWidget):
                if dockWid.isVisible and (mw.dockWidgetArea(dockWid) is area):
                    object = mw.findChildren(QtCore.QObject, dockWid.objectName()+"minMax")
                    Icon = QtGui.QIcon(path+'Pin')
                    self.orgHeight = dockWid.size().height()
                    self.orgWidth = dockWid.size().width()
                    self.minimizeBtn.setIcon(Icon)
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
        dock.setFeatures(self.visible)
        self.title.setText(dock.windowTitle())
        self.docked = False
        self.modifyDock(dock, self.orgWidth, self.orgHeight)


    def collapsedDock(self, dock, area):
        self.side = False
        self.docked = True

        if (area is QtCore.Qt.LeftDockWidgetArea) or \
            (area is QtCore.Qt.RightDockWidgetArea):
            self.side = True
            dock.setTitleBarWidget = self.orgTitle
            text = "\n".join(dock.windowTitle()) + " "
            self.title.setText(text)
            features = QtWidgets.QDockWidget.DockWidgetFeatures(
                self.visible | QtWidgets.QDockWidget.DockWidgetVerticalTitleBar)
            dock.setFeatures(features)
        TBHeight = 24
        # Segmantation fault
        #TBHeight = dock.style().pixelMetric(
        #       QtWidgets.QStyle.PM_TitleBarHeight)
        self.modifyDock(dock, TBHeight, TBHeight)

    def modifyDock(self, dock, width, height):
        if self.side:
            dock.setMinimumWidth(width-1)
            dock.setMaximumWidth(width)
        else:
            dock.setMinimumHeight(height-1)
            dock.setMaximumHeight(height)


    def onClose(self):
        self.deleteLater()

def run():
    for dock in mw.findChildren(QtWidgets.QDockWidget):
        #if dock.windowTitle() == "Report view":continue
        if dock.windowTitle() == "Modern Menu":continue
        ModernDock(dock)
