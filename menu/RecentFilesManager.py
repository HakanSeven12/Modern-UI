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



# RecentFilesManager.py
# Contains classes related to the recent files manager


import sys

from PySide2 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt



class QRecentFilesManager(QtCore.QObject):
    """
    An object that keeps track of paths to recently-opened files
    """
    
    _masterList = []
    _maxLength = 10
    pathAdded = QtCore.Signal(str)
    
    def __init__(self, data=None):
        """
        Initialize the QRecentFilesManager
        """
        QtCore.QObject.__init__(self)
        if data != None: self._initFromData(data)

    def _initFromData(self, data):
        """
        Populate self._masterList from the given string info
        """
        data = str(data)
        if data[:19] != 'QRecentFilesManager:': return
        data = data[19:]

        # Split it
        newlist = data.split('|')

        self._masterList = newlist

    def _generateData(self):
        """
        Generate string info and return it
        """

        # Create a datastr
        datastr = 'QRecentFilesManager:'
        # Add entries
        for entry in self._masterList:
            datastr += entry + '|'
        # Chop off the last '|'
        datastr = datastr[:-1]

        # Return it
        return datastr

    def addPath(self, path):
        """
        Add a path to the path list.
        Automatically remove duplicates.
        """
        if path in (None, 'None', 'none', True, 'True', 'true', False, 'False', 'false', 0, 1, ''): return
        path = path.replace('\\', '/')
        
        # Remove it, if it's already there
        if path in self._masterList: self._masterList.remove(path)
        
        # Prepend it
        new = []
        new.append(path)
        for other in self._masterList: new.append(other)
        if len(new) > self._maxLength: new = new[:self._maxLength]
        self._masterList = new

        # Emit the pathAdded signal
        self.pathAdded.emit(path)

    def data(self):
        """
        Return data that can later be used to run populateFromData
        """
        return self._generateData()

    def maxLength(self):
        """
        Return the maximum number of paths that can be stored
        """
        return self._maxLength

    def paths(self):
        """
        Return the full list of paths
        """
        toReturn = []
        for path in self._masterList:
            toReturn.append(path)
        return toReturn

    def populateFromData(self, data):
        """
        Populate the filepath list from the data given
        """
        self._initFromData(data)

    def setMaxLength(self, length):
        """
        Set the maximum number of paths that can be stored
        """
        self._maxLength = length


