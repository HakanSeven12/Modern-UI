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

mv = FreeCADGui.getMainWindow()

class ModernDock(QtCore.QObject):
    side = False
    docked = True
    AHEnable = 0
    target = None
    AHD = None

    def __init__(self, dock, AHD):
        super(ModernDock, self).__init__(dock)
        dock.installEventFilter(self)
        AHD.installEventFilter(self)
        self.visible = dock.features()
        self.orgHeight = dock.sizeHint().height()
        self.orgWidth = dock.sizeHint().width()
        area = mv.dockWidgetArea(dock)
        self.collapsedDock(dock, area)
        self.target = dock
        self.AHD = AHD

    def eventFilter(self, source, event):
        area = mv.dockWidgetArea(self.target)
        if (source is self.AHD) and (event.type() is event.MouseButtonPress):
            self.AHEnable = (self.AHEnable + 1) % 2

            if self.AHEnable:
                self.openDock(self.target)
                self.target.removeEventFilter(self)
            else:
                self.collapsedDock(self.target, area)
                self.target.installEventFilter(self)

        elif source is self.target:
            if (event.type() is event.Enter) or \
                (self.target.isFloating() and self.docked):
                for dockWid in mv.findChildren(QtWidgets.QDockWidget):
                    if dockWid.isVisible and (mv.dockWidgetArea(dockWid) is area):
                        self.openDock(dockWid)
                return True

            elif event.type() is event.Leave:
                for dockWid in mv.findChildren(QtWidgets.QDockWidget):
                    if dockWid.isVisible and (mv.dockWidgetArea(dockWid) is area):
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

def run():
    AHD = QtWidgets.QPushButton("AH")
    mv.statusBar().addPermanentWidget(AHD)
    mv.statusBar().setVisible(True)

    for dock in mv.findChildren(QtWidgets.QDockWidget):
        ModernDock(dock, AHD)

        """
        title_bar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        title_bar.setLayout(layout)
        button = QtWidgets.QToolButton()
        layout.addWidget(button)
        icon = dock.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMaxButton, widget=dock)
        button.setIcon( icon )
        dock.setTitleBarWidget(title_bar)
        """
