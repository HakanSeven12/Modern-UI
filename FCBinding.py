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

import FreeCAD, FreeCADGui
from menu.ModernMenu import QModernMenu
from PySide2 import QtCore, QtGui, QtWidgets
from Preferences import Preferences
from dock import ModernDock
import os

mw = FreeCADGui.getMainWindow()
p = FreeCAD.ParamGet("User parameter:BaseApp/ModernUI")
path = os.path.dirname(__file__) + "/Resources/icons/"

class MenuDock(QtWidgets.QDockWidget):
    """
    Create QDockWidget for ModernMenu.
    """

    def __init__(self):
        super(MenuDock, self).__init__(mw, QtCore.Qt.FramelessWindowHint)
        self.setObjectName("Modern Menu")
        self.setWindowTitle("Modern Menu")
        self.setTitleBarWidget(QtWidgets.QWidget())
        self.setWidget(ModernMenu())


class ModernMenu(QModernMenu):
    """
    Create ModernMenu QWidget.
    """
    actions = {}
    Enabled = {}

    def __init__(self):
        """
        Constructor
        """
        icon = QtGui.QIcon(":/icons/freecad")
        super(ModernMenu, self).__init__(icon, 'FreeCAD')
        self._tabBar.currentChanged.connect(self.selectWorkbench)
        self.createModernMenu()
        self.createFileMenu()
        self.show()

    def getParameters(self):
        """
        Get saved parameters.
        """
        enabled = p.GetString("Enabled")
        enabled = enabled.split(",")
        partially = p.GetString("Partially")
        partially = partially.split(",")
        unchecked = p.GetString("Unchecked")
        unchecked = unchecked.split(",")
        position = p.GetString("Position")
        position = position.split(",")
        return enabled

    def createModernMenu(self):
        """
        Create menu tabs.
        """
        EnabledList = self.getParameters()
        WBList = FreeCADGui.listWorkbenches()
        for Enabled in EnabledList:
            if Enabled == 'NoneWorkbench': continue
            Icon = self.getWBIcon(WBList[Enabled].Icon)
            Name = WBList[Enabled].MenuText
            self.actions[Name] = Enabled
            self.Enabled[Name] = False
            self.addTab(Icon, Name)

    def createFileMenu(self):
        """
        Add file, macro toolbars and settings to file menu and add recent files.
        """
        # Add file and macro toolbars to file menu
        fileMenu = ['File', 'Macro']
        for toolbar in fileMenu:
            TB = mw.findChildren(QtWidgets.QToolBar, toolbar)
            for button in TB[0].findChildren(QtWidgets.QToolButton):
                if button.text() == '': continue
                self._QFileMenu.addButton(
                    icon=button.icon(), title=button.text(), handler=button.defaultAction().triggered,
                    shortcut=button.shortcut(), statusTip=button.statusTip())

        # Add settings to file menu
        self._QFileMenu.addButton(
            icon= path+'Settings.svg', title='Modern Settings',handler=Preferences, 
            statusTip='Set Modern Menu Preferences')
        
        # Add recent files
        fileList = self.getRecentFiles()
        for file in fileList:
            self._QFileMenu._recentFilesMgr.addPath(file)
            self._QFileMenu.recentFileClicked.connect(self.openFile)

    def getRecentFiles(self):
        """
        Return recent files list.
        """
        fileList = []
        rf = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/RecentFiles")
        rfcount = rf.GetInt("RecentFiles",0)
        for i in range(rfcount):
            filename = rf.GetString("MRU%d" % (i))
            fileList.append(filename)
        return fileList

    def openFile(self, path):
        """
        Open given file in FreeCAD.
        """
        try:
            FreeCAD.openDocument(path)
        except Exception:
            print('File not found')

    def selectWorkbench(self):
        """
        Import selected workbench toolbars to ModernMenu section.
        """
        # Hide selected workbench toolbars
        for tbb in mw.findChildren(QtWidgets.QToolBar):
            tbb.hide()

        # Get selected tab
        Defaults = ['File', 'Workbench', 'Macro', 'View', 'Structure']
        index = self._tabBar.currentIndex()
        tabName = self._tabBar.tabText(index)
        if self.Enabled[tabName]: return
        tab = self._tabs[index]

        # Activate selected workbench
        if tabName == 'FreeCAD': return
        FreeCADGui.activateWorkbench(self.actions[tabName])
        workbench = FreeCADGui.activeWorkbench()

        # Import active workbench toolbars to menu sections
        for toolbar in workbench.listToolbars():
            if toolbar in Defaults: continue
            section = tab.addSection(toolbar)

            # Import toolbars buttons to menu buttons
            TB = mw.findChildren(QtWidgets.QToolBar, toolbar)
            for button in TB[0].findChildren(QtWidgets.QToolButton):
                if button.text() == '': continue
                section.addButton(
                    full=False, icon=button.icon(), title=button.text()+' ', handler=button.defaultAction().triggered,
                    shortcut=button.shortcut(), statusTip=button.statusTip(), menu=button.menu())
        self.Enabled[tabName] = True

    def getWBIcon(self, icon):
        """
        Return workbench icon
        """
        if str(icon.find("XPM")) != "-1":
            Icon = []
            for a in ((((icon
                        .split('{', 1)[1])
                        .rsplit('}', 1)[0])
                    .strip())
                    .split("\n")):
                Icon.append((a
                            .split('"', 1)[1])
                            .rsplit('"', 1)[0])
            Icon = QtGui.QIcon(QtGui.QPixmap(icon))
        else:
            Icon = QtGui.QIcon(QtGui.QPixmap(icon))
        if Icon.isNull():
            Icon = QtGui.QIcon(":/icons/freecad")
        return Icon



    
class run:
    """
    Activate Modern UI.
    """
    def __init__(self, name):
        """
        Constructor
        """
        disable = 0
        if name != "NoneWorkbench":
            # Disable connection after activation
            mw = FreeCADGui.getMainWindow()
            mw.workbenchActivated.disconnect(run)
            if disable: return
            ModernDock.run()
            mw.addDockWidget(
                QtCore.Qt.TopDockWidgetArea, MenuDock())
