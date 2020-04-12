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



# FileMenu.py
# Contains classes related to the file menu


import sys

from PySide2 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

from menu.common import createButton, createHorzLine
from menu.RecentFilesManager import QRecentFilesManager



class QFileMenu(QtWidgets.QMenu):
    """
    A menu that acts like a standard modern File menu
    """
    
    _arrowBtns = []
    _panels = []
    _recentFilesMgr = QRecentFilesManager()
    _recentFilesText = 'Recent files'
    _shortcutAdded = QtCore.Signal()
    _shortcuts = []
    recentFileClicked = QtCore.Signal(str)
    
    def __init__(self):
        """
        Initialize the QFileMenu
        """
        QtWidgets.QMenu.__init__(self)
        minHeight = 384
        self._recentFilesMgr.pathAdded.connect(self._populateRecentFilesPanel)

        # Create a button widget
        btnWidget = QtWidgets.QFrame()
        sp = btnWidget.sizePolicy()
        sp.setVerticalPolicy(sp.Expanding)
        btnWidget.setSizePolicy(sp)
        btnWidget.setMinimumHeight(minHeight)
        self._btnLayout = QtWidgets.QVBoxLayout()
        self._btnLayout.setSpacing(0)
        self._btnLayout.setContentsMargins(0, 0, 0, 0)
        masterLayout = QtWidgets.QVBoxLayout()
        masterLayout.setSpacing(0)
        masterLayout.setContentsMargins(0, 0, 0, 0)
        masterLayout.addLayout(self._btnLayout)
        masterLayout.addStretch(1)
        btnWidget.setLayout(masterLayout)

        # Create a dynamic content widget
        self._dynContentStack = QtWidgets.QStackedWidget()
        self._dynContentStack.setMinimumWidth(256)
        sp = self._dynContentStack.sizePolicy()
        sp.setVerticalPolicy(sp.Expanding)
        self._dynContentStack.setSizePolicy(sp)
        self._dynContentStack.setMinimumHeight(minHeight)

        # Add a recent files menu to the dyn content widget
        self._populateRecentFilesPanel()

        # Create a spacer widget for the bottom
        btmSpacer = QtWidgets.QFrame()
        btmSpacer.setMinimumHeight(12)

        # Main layout
        mL = QtWidgets.QGridLayout()
        mL.setSpacing(0)
        mL.setContentsMargins(0, 0, 0, 0)
        mL.addWidget(btnWidget, 0, 0)
        mL.addWidget(self._dynContentStack, 0, 1)
        mL.addWidget(btmSpacer, 1, 0, 1, 2)

        # Add all of that as a widget action
        w = QtWidgets.QWidget()
        w.setLayout(mL)
        wa = QtWidgets.QWidgetAction(None)
        wa.setDefaultWidget(w)
        self.clear()
        self.addAction(wa)
        self._widgetAction = wa

        # Change the button widget bg color
        btnWidget.setAutoFillBackground(True)
        p = btnWidget.palette()
        p.setColor(p.Window, p.color(p.Base))
        btnWidget.setPalette(p)

        # Set the frame styles
        for w in (btnWidget, self._dynContentStack):
            w.setFrameStyle(QtWidgets.QFrame.Sunken | QtWidgets.QFrame.Box)
            w.setLineWidth(1)

        # Final setup stuff
        self._setDynContentRecentFiles()
        self.aboutToShow.connect(self._handleShow)

    def _addBtn(self, w):
        """
        Add a button to the bottom of the buttons layout
        """
        self._btnLayout.addWidget(w)

    def _handleArrowBtnClicked(self, checked, idx):
        """
        Handle the user clicking an arrow button
        """
        if not checked:
            self._dynContentStack.setCurrentIndex(0)
        else:
            # Deselect all other buttons
            for btnidx in range(len(self._arrowBtns)):
                if btnidx == (idx-1): continue
                self._arrowBtns[btnidx].setChecked(False)
            # Update the dyn content stack
            self._dynContentStack.setCurrentIndex(idx)

    def _handleRecentFileAdded(self):
        """
        Handle a new entry being added to self._recentFilesMgr
        """
        self._populateRecentFilesPanel()
        self._dynContentStack.setCurrentIndex(0)

    def _handleShortcut(self, button):
        """
        Handle the user typing a keyboard shortcut for a button
        """
        button.click()

    def _handleShortcutAddedToPanel(self):
        """
        Handle a shortcut being added to a panel
        """
        for p in self._panels:
            for s in p._shortcuts: self._shortcuts.append(s)
        self._shortcutAdded.emit()

    def _handleShow(self):
        """
        Handle the menu being opened
        """
        self._setDynContentRecentFiles()
        for btn in self._arrowBtns: btn.setChecked(False)

    def _handleRecentFileClick(self, path):
        """
        Handle a user clicking a recent files entry
        """
        print('click path')
        print(path)
        self.recentFileClicked.emit(path)

    def _populateRecentFilesPanel(self):
        """
        Populate the Recent Files panel from self._recentFilesMgr
        """
        # Reset the panel
        self._resetRecentFilesWidget()
        
        # Iterate through each path
        if self._recentFilesMgr == None: pths = []
        else: pths = self._recentFilesMgr.paths()
        idx = 1
        print(pths)
        for pth in pths:
            if idx > 10: break
            # Pick a title string to use
            title = pth.split('/')[-1]
            
            # Create a toolbutton
            btn = QtWidgets.QToolButton()
            btn.setText(title)
            btn.setToolTip(pth)
            btn.setAutoRaise(True)
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setShortcut(str(idx))
            sp = btn.sizePolicy()
            sp.setHorizontalPolicy(sp.Expanding)
            btn.setSizePolicy(sp)
            btn.clicked.connect(lambda: self._handleRecentFileClick(pth))

            # Create an icon
            pix = QtGui.QPixmap(16, 16)
            pix.fill(QtGui.QColor.fromRgb(0,0,0,0))
            ptr = QtGui.QPainter(pix)
            f = btn.font()
            f.setUnderline(True)
            ptr.setFont(f)
            ptr.drawText(0, 12, '%d'%idx)
            del ptr
            btn.setIcon(QtGui.QIcon(pix))
            
            # Add the toolbutton
            self._recentFilesLayout.addWidget(btn)
            idx += 1

    def _resetRecentFilesWidget(self):
        """
        Create a new Recent Files widget
        """
        # Get the old recent files widget
        oldWidget = self._dynContentStack.widget(0)
        
        # Create a new layout to add recent file toolbuttons to
        RFL = QtWidgets.QVBoxLayout()
        RFL.setSpacing(0)
        RFL.setContentsMargins(0, 0, 0, 0)
        RFL.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Set that to a widget
        RFLw = QtWidgets.QWidget()
        RFLw.setLayout(RFL)
        sp = RFLw.sizePolicy()
        sp.setVerticalPolicy(sp.Expanding)
        RFLw.setSizePolicy(sp)
        
        # Make a label
        label = QtWidgets.QLabel(self._recentFilesText)
        f = label.font()
        f.setWeight(f.Bold)
        label.setFont(f)
        label.setEnabled(False)
        self._recentFilesLabel = label
        
        # Make an overall layout
        L = QtWidgets.QVBoxLayout()
        L.setSpacing(4)
        L.setContentsMargins(4, 4, 4, 4)
        L.addWidget(label)
        L.addWidget(createHorzLine())
        L.addWidget(RFLw)
        L.setAlignment(Qt.AlignTop)
        
        # Make a widget for that
        w = QtWidgets.QWidget()
        w.setLayout(L)
        
        # Remove the old widget
        if oldWidget != 0: self._dynContentStack.removeWidget(oldWidget)
        
        # Set the new one in its place
        self._dynContentStack.insertWidget(0, w)
        
        # Assign it to self._recentFilesLayout
        self._recentFilesLayout = RFL

    def _setDynContentRecentFiles(self):
        """
        Set the dynamic content stack to Recent Files mode
        """
        self._dynContentStack.setCurrentIndex(0)

    def addButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a button to the bottom
        """
        btn = createButton(icon, title, handler, shortcut, statusTip)

        # shortcut stuff
        if shortcut != None:
            sh = QtWidgets.QShortcut(shortcut, self)
            sh.activated.connect(lambda arg=btn: self._handleShortcut(arg))
            self._shortcuts.append(sh)
            self._shortcutAdded.emit()

        self._addBtn(btn)
        return btn

    def addArrowButton(self, panel, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a button with an arrow to the bottom
        """
        btn = createButton(icon, title, handler, shortcut, statusTip)
        self._panels.append(panel)

        # Add an arrowbutton
        arrowBtn = QtWidgets.QToolButton()
        arrowBtn.setAutoRaise(True)
        sp = arrowBtn.sizePolicy()
        sp.setVerticalPolicy(sp.Expanding)
        arrowBtn.setSizePolicy(sp)
        arrowBtn.setArrowType(Qt.RightArrow)
        arrowBtn.setCheckable(True)
        self._arrowBtns.append(arrowBtn)

        # Add it to self.arrowBtns, and set up a handler
        idx = self._dynContentStack.addWidget(panel)
        arrowBtn.clicked.connect(lambda checked, idxarg=idx: self._handleArrowBtnClicked(checked, idxarg))

        # Final setup
        L = QtWidgets.QHBoxLayout()
        L.setSpacing(0)
        L.setContentsMargins(0, 0, 0, 0)
        L.addWidget(btn)
        L.addWidget(arrowBtn)
        w = QtWidgets.QWidget()
        w.setLayout(L)
        self._addBtn(w)

        # Do stuff with the shortcut
        if shortcut != None:
            sh = QtWidgets.QShortcut(shortcut, self)
            sh.activated.connect(lambda arg=btn: self._handleShortcut(arg))
            self._shortcuts.append(sh)
            self._shortcutAdded.emit()
        panel._shortcutAdded.connect(self._handleShortcutAddedToPanel)
        for s in panel._shortcuts: self._shortcuts.append(s)
        self._shortcutAdded.emit()
        
        return w

    def addSeparator(self):
        """
        Add a separator to the bottom
        """
        h = createHorzLine()
        h.setMinimumWidth(128)
        h.setMaximumWidth(128)
        self._addBtn(h)
        self._btnLayout.setAlignment(h, Qt.AlignRight)

    def RecentFilesManager(self):
        """
        Return the QRecentFilesManager currently in use
        """
        return self._recentFilesMgr

    def recentFilesText(self):
        """
        Return the current 'Recent files' text
        """
        return self._recentFilesText

    def setRecentFilesManager(self, manager):
        """
        Set a recent files manager to be used
        """
        if not isinstance(manager, QRecentFilesManager): return False
        self._recentFilesMgr = manager
        manager.pathAdded.connect(self._handleRecentFileAdded)

        self._populateRecentFilesPanel()
        self._dynContentStack.setCurrentIndex(0)

    def setRecentFilesText(self, text):
        """
        Set the text of the 'Recent files' label
        """
        text = str(text)
        self._recentFilesText = text
        self._recentFilesLabel.setText(text)





class QFileMenuPanel(QtWidgets.QWidget):
    """
    A widget that acts like a standard right-side button list
    panel in a standard modern File menu
    """
    
    _shortcutAdded = QtCore.Signal()
    _shortcuts = []
    
    def __init__(self, title=''):
        """
        Initialize the QFileMenuPanel
        """
        QtWidgets.QWidget.__init__(self)

        sp = self.sizePolicy()
        sp.setVerticalPolicy(sp.Expanding)
        sp.setHorizontalPolicy(sp.Expanding)
        self.setSizePolicy(sp)

        self._titleLabel = QtWidgets.QLabel(title)
        f = self._titleLabel.font()
        f.setWeight(f.Bold)
        self._titleLabel.setFont(f)
        self._titleLabel.setEnabled(False)

        self._mainLayout = QtWidgets.QVBoxLayout()
        self._mainLayout.setSpacing(0)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        masterLayout = QtWidgets.QVBoxLayout()
        masterLayout.setSpacing(4)
        masterLayout.setContentsMargins(4, 4, 4, 4)
        masterLayout.addWidget(self._titleLabel)
        masterLayout.addWidget(createHorzLine())
        masterLayout.addLayout(self._mainLayout)
        masterLayout.addStretch(1)
        self.setLayout(masterLayout)

    def _handleShortcut(self, button):
        """
        Handle the user typing a keyboard shortcut
        """
        button.click()

    def addButton(self, icon=None, title='', handler=None, shortcut=None, statusTip=None):
        """
        Add a button to the bottom
        """
        btn = createButton(icon, title, handler, shortcut, statusTip)
        self._mainLayout.addWidget(btn)
        if shortcut != None:
            sh = QtWidgets.QShortcut(shortcut, self)
            sh.activated.connect(lambda arg=btn: self._handleShortcut(arg))
            self._shortcuts.append(sh)
            self._shortcutAdded.emit()
        return btn

    def setTitle(self, title):
        """
        Set the title
        """
        title = str(title)
        self._titleLabel.setText(title)

    def title(self):
        """
        Return the title
        """
        return str(self._titleLabel.text())

