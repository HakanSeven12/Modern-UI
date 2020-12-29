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



# common.py
# Contains functions used in various places by the library, but
# not intended to be used by other applications


import sys

from PySide2 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt



def createButton(icon=None, title='', handler=None, shortcut=None, statusTip=None, menu=None):
    """
    Create and return a QToolButton with the given options
    """
    btn = QtWidgets.QToolButton()
    btn.setAutoRaise(True)

    # generate a tooltip
    tt = '<b>' + title
    if shortcut != None:
        if isinstance(shortcut, str):
            tt += ' (' + shortcut + ')'
        elif isinstance(shortcut, QtGui.QKeySequence.StandardKey):
            bindings = QtGui.QKeySequence.keyBindings(shortcut)
            s = ''
            for b in bindings:
                s += b.toString() + ', '
            s = s[0:-2]
            if len(s) > 0:
                tt += ' (' + s + ')'
        elif isinstance(shortcut, QtGui.QKeySequence):
            tt += ' (' + str(shortcut.toString()) + ')'
    tt += '</b>'
    if statusTip != None:
        tt += '<br><br>' + statusTip
        # &nbsp;&nbsp; gives it a 2-space indent
    btn.setToolTip(tt)

    # size
    btn.setIconSize(QtCore.QSize(24, 24))
    sp = btn.sizePolicy()
    sp.setHorizontalPolicy(sp.Expanding)
    btn.setSizePolicy(sp)

    # icon
    if icon != None:
        icon = QtGui.QIcon(icon)
        btn.setIcon(icon)

    # title
    if title != None:
        btn.setText(title)
    btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    # handler
    if handler != None:
        btn.clicked.connect(handler)

    # shortcut
    if shortcut != None:
        btn.setShortcut(shortcut)

    # statusTip
    if statusTip != None:
        btn.setStatusTip(statusTip)

    # menu
    if menu != None:
        btn.setMenu(menu)
        btn.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

    return btn




# From Reggie! Level Editor
def createHorzLine():
    """
    Create and return a horizontal line widget
    """
    f = QtWidgets.QFrame()
    f.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
    f.setEnabled(False)
    return f

def createVertLine():
    """
    Create and return a vertical line widget
    """
    f = QtWidgets.QFrame()
    f.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
    f.setEnabled(False)
    return f
