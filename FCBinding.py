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
import draftutils
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
        self.setMinimumHeight(0)
        sp = self.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Ignored)


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
        icon = QtGui.QIcon(path + 'ModernUI')
        super(ModernMenu, self).__init__(icon, 'Modern UI')
        self._tabBar.currentChanged.connect(self.selectWorkbench)
        self.createModernMenu()
        self.createFileMenu()
        self.show()

    def createModernMenu(self):
        """
        Create menu tabs.
        """
        enabledList,positionList = self.getParameters()
        WBList = FreeCADGui.listWorkbenches()
        for position in positionList:
            try:
                if position in enabledList:
                    Icon = self.getWorkbenchIcon(WBList[position].Icon)
                    Name = WBList[position].MenuText
                    self.actions[Name] = position
                    self.Enabled[Name] = False
                    self.addTab(Icon, Name)
            except Exception:
                pass

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
            icon= path+'Settings', title='Modern Settings',handler=Preferences, 
            statusTip='Set Modern Menu Preferences')
        
        # Add recent files
        self._QFileMenu.recentFileClicked.connect(self.openFile)
        fileList = self.getRecentFiles()
        fileList.reverse()
        for file in fileList:
            self._QFileMenu._recentFilesMgr.addPath(file)

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
        print('open path')
        print(path)
        try:
            FreeCAD.openDocument(path)
        except Exception:
            print('File not found')

    def defaultWorkbenches(self):
        """
        Sorted string of available workbenches.
        """
        workbenches = FreeCADGui.listWorkbenches()
        workbenches = list(workbenches)
        workbenches.sort()
        workbenches = ",".join(workbenches)
        return workbenches

    def getParameters(self):
        """
        Get saved parameters.
        """
        default = self.defaultWorkbenches()
        enabled = p.GetString("Enabled", default)
        enabled = enabled.split(",")
        partially = p.GetString("Partially")
        partially = partially.split(",")
        unchecked = p.GetString("Unchecked")
        unchecked = unchecked.split(",")
        position = p.GetString("Position", default)
        position = position.split(",")
        return enabled, position

    def selectWorkbench(self):
        """
        Import selected workbench toolbars to ModernMenu section.
        """
        # Get selected tab
        Defaults = ['File', 'Workbench', 'Macro', 'View', 'Structure']
        index = self._tabBar.currentIndex()
        tabName = self._tabBar.tabText(index)
        tab = self._tabs[index]

        # Activate selected workbench
        tabName = tabName.replace('&', '')
        if tabName == 'Modern UI': return
        FreeCADGui.activateWorkbench(self.actions[tabName])
        workbench = FreeCADGui.activeWorkbench()

        # Hide selected workbench toolbars
        for tbb in mw.findChildren(QtWidgets.QToolBar):
            tbb.hide()
        try:
            draftutils.init_draft_statusbar.show_draft_statusbar()
        except Exception:
            pass

        # Import active workbench toolbars to menu sections
        NORParam = p.GetString("NumberOfRows", "3")
        if NORParam == "3":
            NOR = 3
        elif NORParam == "4":
            NOR = 4
        else:
            NOR = 5

        if self.Enabled[tabName]: return
        for toolbar in workbench.listToolbars():
            if toolbar in Defaults: continue
            section = tab.addSection(toolbar, NOR)

            # Import toolbars buttons to menu buttons
            TB = mw.findChildren(QtWidgets.QToolBar, toolbar)
            for button in TB[0].findChildren(QtWidgets.QToolButton):
                if button.text() == '': continue

                styleParam = p.GetString("IconStyle", "Icon and text")
                if styleParam == "Text":
                    iconStyle=None
                    titleStyle=button.text()+' '
                elif styleParam == "Icon":
                    iconStyle=button.icon()
                    titleStyle=None
                else:
                    iconStyle=button.icon()
                    titleStyle=button.text()+' '

                sizeParam = p.GetString("IconSize", "Small")
                if sizeParam == "Small":
                    size=False
                else:
                    size=True

                section.addButton(
                    full=size, icon=iconStyle, title=titleStyle, handler=button.defaultAction().triggered,
                    shortcut=button.shortcut(), statusTip=button.statusTip(), menu=button.menu())
                #section.addCustomWidget(button, full=False)
        self.Enabled[tabName] = True

    def getWorkbenchIcon(self, icon):
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
            Icon = QtGui.QIcon(QtGui.QPixmap(Icon))
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
            mw.addDockWidget(
                QtCore.Qt.TopDockWidgetArea, MenuDock())
            CollapsDock = p.GetString("CollapsibleDock", "On")
            if CollapsDock == "On": ModernDock.run()
