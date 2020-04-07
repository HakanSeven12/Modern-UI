# ***********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
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

import sys
import FreeCADGui

def runModernUI(name):
    disable = 0
    dev = 1
    
    if name != "NoneWorkbench":
        # Disablle after activation
        mw = FreeCADGui.getMainWindow()
        mw.workbenchActivated.disconnect(runModernUI)
        if disable: return
        print("ModernUI is enabled")
        from dock import ModernDock
        ModernDock.run()
        
        from PySide2 import QtCore, QtGui, QtWidgets
        if dev:
            from CreateMenu import MenuDock
            mw.addDockWidget(
                QtCore.Qt.TopDockWidgetArea, MenuDock())


"""
InitGui.py files are passing function and the runModernUI 
wouldn't be visible outside. So need to be added to __main__
"""

import __main__
__main__.runModernUI = runModernUI

# When WB activated runModernUI() going to work
mw = FreeCADGui.getMainWindow()
mw.workbenchActivated.connect(runModernUI)

