# ************************************************************************
# *                                                                      *
# * PyQtRibbon: a ribbon library for PyQt                                *
# * Copyright (C) 2014 RoadrunnerWMC                                     *
# *                                                                      *
# * This file is part of PyQtRibbon.                                     *
# *                                                                      *
# * PyQtRibbon is free software: you can redistribute it and/or modify   *
# * it under the terms of the GNU General Public License as published by *
# * the Free Software Foundation, either version 3 of the License, or    *
# * (at your option) any later version.                                  *
# *                                                                      *
# * PyQtRibbon is distributed in the hope that it will be useful,        *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of       *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        *
# * GNU General Public License for more details.                         *
# *                                                                      *
# * You should have received a copy of the GNU General Public License    *
# * along with PyQtRibbon.  If not, see <http://www.gnu.org/licenses/>.  *
# *                                                                      *
# ************************************************************************


# Contains classes related to the modern menu itself
from PySide2 import QtCore, QtGui, QtWidgets
from menu.common import createVertLine
from menu.FileMenu import QFileMenu
import sys

Qt = QtCore.Qt

class QModernMenu(QtWidgets.QWidget):
    """
    A widget that acts like a standard modern menu
    """
    
    _helpMenu = None
    _helpIcon = None
    _tabs = [None]
    _tabBarIdx = 1
    _tabChanging = False
    _tabHidden = False
    
    def __init__(self, icon, project):
        """
        Initialize the QModernMenu
        """
        QtWidgets.QWidget.__init__(self)
        self.setFocusPolicy(Qt.ClickFocus)

        # Create a tab bar
        self._tabBar = QtWidgets.QTabBar()
        self._tabBar.setMovable(True)
        self._tabBar.setExpanding(False)
        self._tabBar.currentChanged.connect(self._currentTabChanged)
        self._tabBar.mousePressEvent = self._handleTabBarClick

        # Create a widget stack
        self._stack = QtWidgets.QStackedWidget(self)

        # Create a file menu
        self._QFileMenu = QFileMenu()

        # Create a minimize button
        self._minBtn = QtWidgets.QToolButton()
        self._minBtn.setAutoRaise(True)
        self._minBtn.setArrowType(Qt.UpArrow)
        self._minBtn.clicked.connect(self._handleMinBtnClick)

        # Create a menu for when the QModernMenu is minimized
        self._minMenu = QtWidgets.QMenu()

        # Create a help button
        self._helpBtn = QtWidgets.QToolButton()
        self._helpBtn.setAutoRaise(True)
        self._helpBtn.setVisible(False)
        self._helpBtn.setPopupMode(self._helpBtn.InstantPopup)

        # Set up a tab bar widget with buttons on the right edge
        tbLayout = QtWidgets.QGridLayout()
        tbLayout.setContentsMargins(0, 0, 0, 0)
        tbLayout.setSpacing(0)
        tbLayout.addWidget(self._tabBar,  0, 0, 1, 2)
        tbLayout.addWidget(self._minBtn,  0, 0)
        tbLayout.addWidget(self._helpBtn, 0, 1)
        tbLayout.setAlignment(self._minBtn,  Qt.AlignRight)
        tbLayout.setAlignment(self._helpBtn, Qt.AlignRight)
        tbLayout.setColumnStretch(0, 1)
        tbWidget = QtWidgets.QWidget()
        tbWidget.setLayout(tbLayout)
        tbWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._tabBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._tabLayerWidget = tbWidget

        # Set up a layout
        self._mainLayout = QtWidgets.QGridLayout()
        self._mainLayout.addWidget(tbWidget, 0, 0)
        self._mainLayout.addWidget(self._stack, 1, 0)
        self._mainLayout.setRowStretch(1, 1)
        self._mainLayout.setSpacing(0)
        self._mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self._mainLayout)

        # Add a File tab
        self._tabChanging = True
        self._tabBar.addTab( icon, project)
        self._tabChanging = False

    def _currentTabChanged(self, idx):
        """
        Handle the user changing the current tab
        """
        if self._tabChanging: return
        if idx == 0:
            # This doesn't return until the menu is closed
            self._QFileMenu.exec_(self._tabBar.mapToGlobal(QtCore.QPoint(0, self._tabBar.height())))
            # Now set the tab bar to the previous tab
            self._tabChanging = True
            self._tabBar.setCurrentIndex(self._tabBarIdx)
            self._tabChanging = False
        else:
            self._stack.setCurrentIndex(idx - 1)
            self._tabBarIdx = idx

    def _handleMinBtnClick(self):
        """
        Handle the user clicking the minimize/pin button
        """
        if self._tabHidden:
            # The user clicked the button in its "maximize QModernMenu" state
            self._tabHidden = False
            self._minBtn.setArrowType(Qt.UpArrow)

            # Change the layout stuff
            self._minMenuLayout.removeWidget(self._stack)
            self._mainLayout.addWidget(self._stack, 1, 0)
        else:
            # The user clicked the button in its "minimize QModernMenu" state
            self._tabHidden = True
            self._minBtn.setArrowType(Qt.DownArrow)
            self._tabBar.setCurrentIndex(-1)

            # Change the layout stuff
            self._mainLayout.removeWidget(self._stack)

            self._minMenuLayout = QtWidgets.QHBoxLayout()
            self._minMenuLayout.setSpacing(0)
            self._minMenuLayout.setContentsMargins(0,0,0,0)
            self._minMenuLayout.addWidget(self._stack)
            w = QtWidgets.QWidget()
            w.setLayout(self._minMenuLayout)
            wa = QtWidgets.QWidgetAction(None)
            wa.setDefaultWidget(w)
            self._minMenu.clear()
            self._minMenu.addAction(wa)
            self._widgetAction = wa # prevents bugs

    def _handleTabBarClick(self, event):
        """
        Handle the user clicking the tab bar
        """
        if self._tabChanging: return
        QtWidgets.QTabBar.mousePressEvent(self._tabBar, event)
        if self._tabHidden: self._showTabMenu()

    def _handleShortcutAdded(self):
        """
        Handle a shortcut being added to a QModernSection
        """
        for tab in self._tabs:
            if tab == None: continue
            for sh in tab._shortcuts():
                sh.setParent(self)

        if self._QFileMenu != None:
            for sh in self._QFileMenu._shortcuts:
                sh.setParent(self)

    def _showTabMenu(self):
        """
        Display the menu containing the tab content
        If the modern menu is not minimized, does nothing
        """
        if not self._tabHidden: return
        self._minMenu.setMinimumWidth(self._tabBar.width())
        self._minMenu.exec_(self._tabBar.mapToGlobal(QtCore.QPoint(0, self._tabBar.height())))

    def _tabTitleChanged(self, tab, newTitle):
        """
        Handle the title of a tab being changed
        """
        try: idx = self.tabs.index(tab)
        except: return
        self.tabBar.setTabText(idx, newTitle)

    def addTab(self, icon, title):
        """
        Add a tab to the end of the modern menu
        """
        tab = QModernTab(title)
        self._tabs.append(tab)
        self._tabBar.addTab(icon, title)
        tab._titleChanged.connect(self._tabTitleChanged)
        tab._shortcutAdded.connect(self._handleShortcutAdded)
        #self._handleShortcutAdded()

        scrl = QtWidgets.QScrollArea()
        scrl.setFrameStyle(QtWidgets.QFrame.NoFrame)
        scrl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrl.setWidget(tab)
        scrl.setWidgetResizable(True)
        self._stack.addWidget(scrl)

        if len(self._tabs) == 2:
            self._tabChanging = True
            self._tabBar.setCurrentIndex(1)
            self._tabChanging = False
            self._stack.setCurrentIndex(0)
        return tab

    def helpIcon(self):
        """
        Return the help button icon
        """
        return self._helpIcon

    def helpMenu(self):
        """
        Return the help menu
        """
        return self._helpMenu

    def fileMenu(self):
        """
        Return the file menu
        """
        return self._QFileMenu

    def fileTitle(self):
        """
        Return the title of the File tab
        """
        return str(self._tabBar.tabText(0))

    def setFileMenu(self, menu):
        """
        Sets the file menu
        """
        self._QFileMenu = menu
        self._QFileMenu._shortcutAdded.connect(self._handleShortcutAdded)
        self._handleShortcutAdded()

    def setFileTitle(self, title):
        """
        Set the title of the File tab
        """
        self._tabBar.setTabText(0, title)

    def setHelpIcon(self, icon):
        """
        Set the help button icon
        """
        self._helpIcon = icon
        self._helpBtn.setIcon(icon)

    def setHelpMenu(self, menu):
        """
        Set the help menu
        """
        self._helpMenu = menu
        self._helpBtn.setVisible(True)
        self._helpBtn.setMenu(menu)

        # Attempt to remove the down arrow
        #option = QtWidgets.QStyleOptionToolButton()
        #self._helpBtn.initStyleOption(option)
        #option.features |= QtWidgets.QStyleOptionToolButton.MenuButtonPopup
        #self._helpBtn.seyStyleOption(option)










class QModernTab(QtWidgets.QWidget):
    """
    A widget that acts like a standard modern menu tab content area
    """

    _orientation = Qt.Horizontal
    _sections = []
    _shortcutAdded = QtCore.Signal()
    _title = ''
    _titleChanged = QtCore.Signal()
    
    def __init__(self, title):
        """
        Initialize the QModernTab
        """
        QtWidgets.QWidget.__init__(self)

        self._title = title

        self._mainLayout = QtWidgets.QHBoxLayout()
        self._mainLayout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(self._mainLayout)

    def _handleShortcutAdded(self):
        """
        Alerts the QModernMenu associated with this QModernTab that a
        shortcut has been added
        """
        self._shortcutAdded.emit()

    def _regenerateLayout(self):
        """
        Regenerates the layout
        """
        pass

    def _shortcuts(self):
        """
        Return all shortcuts of the current QModernSections
        """
        shortcuts = []
        for sect in self._sections:
            for sh in sect._shortcuts: shortcuts.append(sh)
        return shortcuts

    def addSection(self, title):
        """
        Add a QModernSection to the end
        """
        section = QModernSection(title)
        self._sections.append(section)

        section._shortcutAdded.connect(self._handleShortcutAdded)
        #self._handleShortcutAdded()

        vline = createVertLine()
        vline.setEnabled(True)

        c = self._mainLayout.count()
        if c != 0: self._mainLayout.takeAt(c-1)
        self._mainLayout.addWidget(section)
        self._mainLayout.addWidget(vline)
        self._mainLayout.addStretch(1)

        return section

    def orientation(self):
        """
        Return the orientation that will be used for
        arranging small buttons
        """
        return self._orientation

    def setOrientation(self, orientation):
        """
        Set the orientation that will be used for
        arranging small buttons
        """
        self._orientation = orientation
        self._regenerateLayout()

    def setTitle(self, title):
        """
        Set the title
        """
        self._title = title
        self._titleChanged.emit(self, title)

    def title(self):
        """
        Return the title
        """
        return self._title










class QModernSection(QtWidgets.QWidget):
    """
    A widget that acts like a modern menu tab shortcut container
    """
    
    _widgetRow = 0
    _widgetCol = 0
    _shortcutAdded = QtCore.Signal()
    _shortcuts = []
    
    def __init__(self, title):
        """
        Initialize the QModernSection
        """
        QtWidgets.QWidget.__init__(self)

        self._titleLabel = QtWidgets.QLabel(title)
        self._titleLabel.setEnabled(False) # grays it out

        # self._mainLayout is inside masterLayout
        # so that changes to self._mainLayout won't
        # affect self._titleLabel

        self._mainLayout = QtWidgets.QGridLayout()
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._mainLayout.setSpacing(0)

        masterLayout = QtWidgets.QVBoxLayout()
        masterLayout.setContentsMargins(0, 0, 0, 0)
        masterLayout.setSpacing(0)
        masterLayout.addLayout(self._mainLayout)
        masterLayout.addWidget(self._titleLabel, 0, Qt.AlignHCenter | Qt.AlignBottom)
        self.setLayout(masterLayout)

    def _addWidget(self, widget, full=True):
        """
        Add a widget to the end
        """
        # "full" is a bool specifying if this widget
        # should span all 3 layout rows or not.

        rowspan = 3 if full else 1
        if full and (self._widgetRow in [1, 2]):
            self._widgetRow = 0
            self._widgetCol += 1
        self._mainLayout.addWidget(widget, self._widgetRow, self._widgetCol, rowspan, 1)
        if full:
            self._widgetRow = 0
            self._widgetCol += 1
        else:
            self._widgetRow += 1
            if self._widgetRow == 3:
                self._widgetRow = 0
                self._widgetCol += 1

    def _handleShortcut(self, button):
        """
        Handles the user clicking a shortcut
        """
        button.click()

    def addCustomWidget(self, widget, full=True):
        """
        Add a custom widget to the end
        """
        self._addWidget(self, widget, full)

    def addButton(self, full=False, icon=None, title=None, handler=None, shortcut=None, statusTip=None, menu=None):
        """
        Add a button to the end
        """
        btn = QtWidgets.QToolButton()
        btn.setAutoRaise(True)

        # full
        s = 32 if full else 16
        btn.setIconSize(QtCore.QSize(s, s))
        if full:
            sp = btn.sizePolicy()
            sp.setVerticalPolicy(sp.Expanding)
            btn.setSizePolicy(sp)

        # icon
        if icon != None:
            icon = QtGui.QIcon(icon)
            btn.setIcon(icon)

        # title
        if title != None:
            btn.setText(title)
        if full: btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        else: btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # handler
        if handler != None:
            btn.clicked.connect(handler)

        # shortcut
        if shortcut != None:
            sh = QtWidgets.QShortcut(shortcut, self)
            sh.activated.connect(lambda arg=btn: self._handleShortcut(arg))
            self._shortcuts.append(sh)
            self._shortcutAdded.emit()

        # statusTip
        if statusTip != None:
            btn.setStatusTip(statusTip)

        # menu
        if menu != None:
            btn.setMenu(menu)
            btn.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

        self._addWidget(btn, full)
        return btn

    def addSmallButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a small button to the end
        """
        return self.addButton(False, icon, title, handler, shortcut, statusTip)

    def addFullButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a full-size button to the end
        """
        return self.addButton(True, icon, title, handler, shortcut, statusTip)

    def addToggleButton(self, full=False, icon=None, title=None, handler=None, shortcut=None, statusTip=None, menu=None):
        """
        Add a togglebutton to the end
        """
        btn = QtWidgets.QToolButton()
        btn.setAutoRaise(True)
        btn.setCheckable(True)

        # full
        s = 32 if full else 16
        btn.setIconSize(QtCore.QSize(s, s))

        # icon
        if icon != None:
            icon = QtGui.QIcon(icon)
            btn.setIcon(icon)

        # title
        if title != None:
            btn.setText(title)
        if full: btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        else: btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # handler
        if handler != None:
            btn.clicked.connect(handler)

        # shortcut
        if shortcut != None:
            sh = QtWidgets.QShortcut(shortcut, self)
            sh.activated.connect(lambda arg=btn: self._handleShortcut(arg))
            self._shortcuts.append(sh)
            self._shortcutAdded.emit()

        # statusTip
        if statusTip != None:
            btn.setStatusTip(statusTip)

        # menu
        if menu != None:
            btn.setMenu(menu)

        self._addWidget(btn, full)
        return btn

    def addSmallToggleButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a small togglebutton to the end
        """
        return self.addToggleButton(False, icon, title, handler, shortcut, statusTip)

    def addFullToggleButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a full-size togglebutton to the end
        """
        return self.addToggleButton(True, icon, title, handler, shortcut, statusTip)

    def setTitle(self, title):
        """
        Set the text of the title label
        """
        self._titleLabel.setText(title)

    def title(self):
        """
        Return the text of the title label
        """
        return str(self._titleLabel.text())

