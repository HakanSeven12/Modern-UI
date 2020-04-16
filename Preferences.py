
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

import FreeCADGui, FreeCAD
from PySide2 import QtCore, QtGui, QtWidgets
import os

class Preferences(QtWidgets.QDialog):
    """
    Preferences dialog.
    """
    actions = {}
    mw = FreeCADGui.getMainWindow()
    group = QtWidgets.QActionGroup(mw)
    p = FreeCAD.ParamGet("User parameter:BaseApp/ModernUI")
    path = os.path.dirname(__file__) + "/Resources/icons/"

    def __init__(self):
        self.workbenchActions()
        super(Preferences, self).__init__(self.mw)
        self.setModal(True)
        self.resize(800, 450)
        self.setWindowTitle("Modern UI Preferences")

        # Create selector
        selector = QtWidgets.QListWidget()
        selector.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Create Button Style options
        iconRB = QtWidgets.QRadioButton("Icon")
        textRB = QtWidgets.QRadioButton("Text")
        iconTextRB = QtWidgets.QRadioButton("Icon and text")
        styleLay = QtWidgets.QVBoxLayout()
        styleLay.addWidget(iconRB)
        styleLay.addWidget(textRB)
        styleLay.addWidget(iconTextRB)
        styleGB = QtWidgets.QGroupBox("Button Style:")
        styleGB.setLayout(styleLay)
        
        # Create Button Size options
        smallRB = QtWidgets.QRadioButton("Small")
        bigRB = QtWidgets.QRadioButton("Big")
        sizeLay = QtWidgets.QVBoxLayout()
        sizeLay.addWidget(smallRB)
        sizeLay.addWidget(bigRB)
        sizeGB = QtWidgets.QGroupBox("Button Size:")
        sizeGB.setLayout(sizeLay)

        # Create Pref button options
        onRB = QtWidgets.QRadioButton("On")
        offRB = QtWidgets.QRadioButton("Off")
        CollapsLay = QtWidgets.QVBoxLayout()
        CollapsLay.addWidget(onRB)
        CollapsLay.addWidget(offRB)
        CollapsGB = QtWidgets.QGroupBox("Collapsible Docks:")
        CollapsGB.setLayout(CollapsLay)

        # Create empty layout
        emptyLay = QtWidgets.QHBoxLayout()
        emptyLay.addStretch()

        # Create Preferences options group box
        prefLay = QtWidgets.QVBoxLayout()
        prefLay.addWidget(styleGB)
        prefLay.addWidget(sizeGB)
        prefLay.addWidget(CollapsGB)
        prefLay.addStretch()
        prefLay.insertLayout(0, emptyLay)

        # Create Close button
        closeBtn = QtWidgets.QPushButton("Close")
        closeBtn.setToolTip("Close the preferences dialog")
        closeBtn.setDefault(True)

        # Create Up button
        upBtn = QtWidgets.QPushButton()
        upBtn.setToolTip("Move selected item up")
        upBtn.setIcon(QtGui.QIcon(self.path + "MoveUp"))
        
        # Create Down button
        downBtn = QtWidgets.QPushButton()
        downBtn.setToolTip("Move selected item down")
        downBtn.setIcon(QtGui.QIcon(self.path + "MoveDown"))

        # Create buttons layout
        btnLay = QtWidgets.QHBoxLayout()
        btnLay.addWidget(upBtn)
        btnLay.addWidget(downBtn)
        btnLay.addStretch(1)
        btnLay.addWidget(closeBtn)

        # Create panel layout
        panelLay = QtWidgets.QHBoxLayout()
        panelLay.addWidget(selector)
        panelLay.insertLayout(1, prefLay)

        # Set Dialog layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.insertLayout(0, panelLay)
        mainLayout.insertLayout(1, btnLay)
        self.setLayout(mainLayout)
        self.show()
        
        # Get saved parameters.
        default = self.defaultWorkbenches()
        enabled = self.p.GetString("Enabled", default)
        enabled = enabled.split(",")
        partially = self.p.GetString("Partially")
        partially = partially.split(",")
        unchecked = self.p.GetString("Unchecked")
        unchecked = unchecked.split(",")
        position = self.p.GetString("Position")
        position = position.split(",")
        default = default.split(",")

        for i in default:
            if i not in position:
                position.append(i)

        for i in position:
            if i in self.actions:
                item = QtWidgets.QListWidgetItem(selector)
                item.setText(self.actions[i].text())
                item.setIcon(self.actions[i].icon())
                item.setData(32, self.actions[i].data())

                if self.actions[i].data() in enabled:
                    item.setCheckState(QtCore.Qt.CheckState(2))
                    item.setData(50, "Checked")
                elif self.actions[i].data() in partially:
                    item.setCheckState(QtCore.Qt.CheckState(1))
                    item.setData(50, "Partially")
                elif self.actions[i].data() in unchecked:
                    item.setCheckState(QtCore.Qt.CheckState(0))
                    item.setData(50, "Unchecked")
                else:
                    item.setCheckState(QtCore.Qt.CheckState(2))
                    item.setData(50, "Checked")

        style = self.p.GetString("IconStyle", "Icon and text")
        if style == "Text":
            textRB.setChecked(True)
        elif style == "Icon":
            iconRB.setChecked(True)
        else:
            iconTextRB.setChecked(True)

        size = self.p.GetString("IconSize", "Small")
        if size == "Small":
            smallRB.setChecked(True)
        else:
            bigRB.setChecked(True)

        CollapsDock = self.p.GetString("CollapsibleDock", "On")
        if CollapsDock == "On":
            onRB.setChecked(True)
        else:
            offRB.setChecked(True)

        # Set connections
        iconRB.toggled.connect(self.onStyleChanged)
        textRB.toggled.connect(self.onStyleChanged)
        iconTextRB.toggled.connect(self.onStyleChanged)
        smallRB.toggled.connect(self.onSizeChanged)
        bigRB.toggled.connect(self.onSizeChanged)
        onRB.toggled.connect(self.onCollapsChanged)
        offRB.toggled.connect(self.onCollapsChanged)
        upBtn.clicked.connect(self.onUpClicked)
        downBtn.clicked.connect(self.onDownClicked)
        selector.itemChanged.connect(self.onItemChanged)
        self.finished.connect(self.onFinished)
        closeBtn.clicked.connect(self.onAccepted)

        self.styleGB = styleGB
        self.sizeGB = sizeGB
        self.CollapsGB = CollapsGB
        self.selector = selector

    def workbenchIcon(self, i):
        """
        Create workbench icon.
        """
        if str(i.find("XPM")) != "-1":
            icon = []
            for a in ((((i
                        .split('{', 1)[1])
                        .rsplit('}', 1)[0])
                    .strip())
                    .split("\n")):
                icon.append((a
                            .split('"', 1)[1])
                            .rsplit('"', 1)[0])
            icon = QtGui.QIcon(QtGui.QPixmap(icon))
        else:
            icon = QtGui.QIcon(QtGui.QPixmap(i))
        if icon.isNull():
            icon = QtGui.QIcon(":/icons/freecad")
        return icon

    def workbenchActions(self):
        """
        Create workbench actions.
        """
        wbList = FreeCADGui.listWorkbenches()
        for i in wbList:
            if i not in self.actions:
                action = QtWidgets.QAction(self.group)
                action.setCheckable(True)
                action.setText(wbList[i].MenuText)
                action.setData(i)
                try:
                    action.setIcon(self.workbenchIcon(wbList[i].Icon))
                except:
                    action.setIcon(QtGui.QIcon(":/icons/freecad"))
                self.actions[i] = action

    def defaultWorkbenches(self):
        """
        Sorted string of available workbenches.
        """
        workbenches = FreeCADGui.listWorkbenches()
        workbenches = list(workbenches)
        workbenches.sort()
        workbenches = ",".join(workbenches)
        return workbenches

    def onAccepted(self):
        """
        Close dialog on button close.
        """
        self.done(1)

    def onFinished(self):
        """
        Delete dialog on close.
        """
        self.deleteLater()

    def onItemChanged(self, item=None):
        """
        Save workbench list state.
        """
        selector = self.selector
        if item:
            selector.blockSignals(True)
            if item.data(50) == "Unchecked":
                item.setCheckState(QtCore.Qt.CheckState(1))
                item.setData(50, "Partially")
            elif item.data(50) == "Partially":
                item.setCheckState(QtCore.Qt.CheckState(2))
                item.setData(50, "Checked")
            else:
                item.setCheckState(QtCore.Qt.CheckState(0))
                item.setData(50, "Unchecked")
            selector.blockSignals(False)
        enabled = []
        partially = []
        unchecked = []
        for index in range(selector.count()):
            if selector.item(index).checkState() == QtCore.Qt.Checked:
                enabled.append(selector.item(index).data(32))
            elif (selector.item(index).checkState() ==
                QtCore.Qt.PartiallyChecked):
                partially.append(selector.item(index).data(32))
            else:
                unchecked.append(selector.item(index).data(32))
        self.p.SetString("Enabled", ",".join(enabled))
        self.p.SetString("Partially", ",".join(partially))
        self.p.SetString("Unchecked", ",".join(unchecked))

    def onUpClicked(self):
        """
        Save workbench position list.
        """
        selector = self.selector
        currentIndex = selector.currentRow()
        if currentIndex != 0:
            selector.blockSignals(True)
            currentItem = selector.takeItem(currentIndex)
            selector.insertItem(currentIndex - 1, currentItem)
            selector.setCurrentRow(currentIndex - 1)
            selector.blockSignals(False)
            position = []
            for index in range(selector.count()):
                position.append(selector.item(index).data(32))
            self.p.SetString("Position", ",".join(position))
            self.onItemChanged(selector)

    def onDownClicked(self):
        """
        Save workbench position list.
        """
        selector = self.selector
        currentIndex = selector.currentRow()
        if currentIndex != selector.count() - 1 and currentIndex != -1:
            selector.blockSignals(True)
            currentItem = selector.takeItem(currentIndex)
            selector.insertItem(currentIndex + 1, currentItem)
            selector.setCurrentRow(currentIndex + 1)
            selector.blockSignals(False)
            position = []
            for index in range(selector.count()):
                position.append(selector.item(index).data(32))
            self.p.SetString("Position", ",".join(position))
            self.onItemChanged(selector)

    def onStyleChanged(self):
        """
        Set Modern Menu style.
        """
        styleGB = self.styleGB
        for i in styleGB.findChildren(QtWidgets.QRadioButton):
            if i.isChecked():
                self.p.SetString("IconStyle", i.text())

    def onSizeChanged(self):
        """
        Set Modern Menu orientation.
        """
        sizeGB = self.sizeGB
        for i in sizeGB.findChildren(QtWidgets.QRadioButton):
            if i.isChecked():
                self.p.SetString("IconSize", i.text())

    def onCollapsChanged(self):
        """
        Set pref button.
        """
        CollapsGB = self.CollapsGB
        for i in CollapsGB.findChildren(QtWidgets.QRadioButton):
            if i.isChecked():
                self.p.SetString("CollapsibleDock", i.text())