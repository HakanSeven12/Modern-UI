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
from menu.FileMenu import QFileMenu, QFileMenuPanel
from menu.RecentFilesManager import QRecentFilesManager
from PySide2 import QtCore, QtGui, QtWidgets
from Preferences import Preferences
from dock import ModernDock
import webbrowser
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
        self.selectWorkbench()

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
        workbench = FreeCADGui.activeWorkbench()
        if not hasattr(workbench,'__Workbench__'): return
        menu_list = workbench.listMenus()
        fileMenu = QFileMenu()
        menuBar = mw.menuBar()
        for action in menuBar.actions():
            if action.data() not in menu_list:continue
            if action.isSeparator():
                fileMenu.addSeparator()

            else:
                panel = QFileMenuPanel(action.text().replace('&', ''))
                fileMenu.addArrowButton(panel, icon=action.icon(), title=action.text())

                for action in action.menu().actions():
                    if action.isSeparator():
                        panel.addSeparator()

                    else:
                        btn = panel.addButton()
                        btn.setDefaultAction(action)

        # Add settings to file menu
        fileMenu.addSeparator()
        fileMenu.addButton(
            icon= path+'Patreon', title='Support Developer',handler=self.open_donation, 
            statusTip='Set Modern Menu Preferences')

        # Add settings to file menu
        fileMenu.addSeparator()
        fileMenu.addButton(
            icon= path+'Settings', title='Modern Settings',handler=Preferences, 
            statusTip='Set Modern Menu Preferences')

        # Add recent files
        fileMenu.recentFileClicked.connect(self.openFile)
        fileList = self.getRecentFiles()
        fileList.reverse()
        RFManager = QRecentFilesManager()
        for file in fileList:
            RFManager.addPath(file)
        fileMenu.setRecentFilesManager(RFManager)
        self.setFileMenu(fileMenu)

    def open_donation(self):
        webbrowser.open('https://www.patreon.com/HakanSeven12')

    def selectWorkbench(self):
        """
        Import selected workbench toolbars to ModernMenu section.
        """
        # Get selected tab
        Defaults = ['Workbench', 'View', 'Macro']
        show = ['File', 'Structure']

        index = self._tabBar.currentIndex()
        tabName = self._tabBar.tabText(index)
        tab = self._tabs[index]

        # Activate selected workbench
        tabName = tabName.replace('&', '')
        if tabName == 'Modern UI': return
        FreeCADGui.activateWorkbench(self.actions[tabName])
        workbench = FreeCADGui.activeWorkbench()

        # Hide selected workbench toolbars
        #mw.menuBar().hide()
        self.createFileMenu()
        for tbb in mw.findChildren(QtWidgets.QToolBar):
            if tbb.objectName() in ["draft_status_scale_widget", "draft_snap_widget"]: continue
            tbb.hide()

        # Import active workbench toolbars to menu sections
        NORParam = p.GetString("NumberOfRows", "3")
        if NORParam == "3":
            NOR = 3
        elif NORParam == "4":
            NOR = 4
        else:
            NOR = 5

        if self.Enabled[tabName]: return
        if not hasattr(workbench,'__Workbench__'): return
        for toolbar in workbench.listToolbars():
            if toolbar in Defaults: continue
            section = tab.addSection(toolbar.replace(tabName+" ", "").capitalize(), NOR)

            # Import toolbars buttons to menu buttons
            TB = mw.findChildren(QtWidgets.QToolBar, toolbar)
            for button in TB[0].findChildren(QtWidgets.QToolButton):
                if button.text() == '': continue
                action = button.defaultAction()

                sizeParam = p.GetString("IconSize", "Small")
                if sizeParam == "Small":
                    size=False
                else:
                    size=True

                btn = section.addButton(full=size, menu=button.menu())
                btn.setDefaultAction(action)

                styleParam = p.GetString("IconStyle", "Icon and text")
                if styleParam == "Text":
                    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)

                elif styleParam == "Icon" or toolbar in show:
                    btn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

        self.Enabled[tabName] = True

    def getParameters(self):
        """
        Get saved parameters.
        """
        workbench_list = [*FreeCADGui.listWorkbenches()]
        workbenches = ",".join(workbench_list)
        enabled = p.GetString("Enabled", workbenches)
        partially = p.GetString("Partially")
        unchecked = p.GetString("Unchecked")
        position = p.GetString("Position", workbenches)

        enabled = enabled.split(",")
        partially = partially.split(",")
        unchecked = unchecked.split(",")
        position = position.split(",")

        for i in workbench_list:
            if i not in enabled and i not in partially and i not in unchecked: 
                enabled.append(i)

                if i not in position:
                    position.append(i)

        return enabled, position

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
