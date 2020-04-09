
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

        # Create Style options
        iconRB = QtWidgets.QRadioButton("Icon")
        textRB = QtWidgets.QRadioButton("Text")
        iconTextRB = QtWidgets.QRadioButton("Icon and text")
        styleLay = QtWidgets.QVBoxLayout()
        styleLay.addWidget(iconRB)
        styleLay.addWidget(textRB)
        styleLay.addWidget(iconTextRB)
        styleGB = QtWidgets.QGroupBox("Style:")
        styleGB.setLayout(styleLay)
        
        # Create Orientation options
        autoRB = QtWidgets.QRadioButton("Auto")
        topRB = QtWidgets.QRadioButton("Top")
        bottomRB = QtWidgets.QRadioButton("Bottom")
        leftRB = QtWidgets.QRadioButton("Left")
        rightRB = QtWidgets.QRadioButton("Right")
        orientLay = QtWidgets.QVBoxLayout()
        orientLay.addWidget(autoRB)
        orientLay.addWidget(topRB)
        orientLay.addWidget(bottomRB)
        orientLay.addWidget(leftRB)
        orientLay.addWidget(rightRB)
        orientGB = QtWidgets.QGroupBox("Tab orientation:")
        orientGB.setLayout(orientLay)

        # Create Pref button options
        onRB = QtWidgets.QRadioButton("On")
        offRB = QtWidgets.QRadioButton("Off")
        onOffLay = QtWidgets.QVBoxLayout()
        onOffLay.addWidget(onRB)
        onOffLay.addWidget(offRB)
        prefBtnGB = QtWidgets.QGroupBox("Preferences button on tabbar:")
        prefBtnGB.setLayout(onOffLay)

        # Create empty layout
        emptyLay = QtWidgets.QHBoxLayout()
        emptyLay.addStretch()

        # Create Preferences options group box
        prefLay = QtWidgets.QVBoxLayout()
        prefLay.addWidget(styleGB)
        prefLay.addWidget(orientGB)
        prefLay.addWidget(prefBtnGB)
        prefLay.addStretch()
        prefLay.insertLayout(0, emptyLay)

        # Create Close button
        closeBtn = QtWidgets.QPushButton("Close")
        closeBtn.setToolTip("Close the preferences dialog")
        closeBtn.setDefault(True)

        # Create Up button
        upBtn = QtWidgets.QPushButton()
        upBtn.setToolTip("Move selected item up")
        upBtn.setIcon(QtGui.QIcon(self.path + "TabBar_MoveUp"))
        
        # Create Down button
        downBtn = QtWidgets.QPushButton()
        downBtn.setToolTip("Move selected item down")
        downBtn.setIcon(QtGui.QIcon(self.path + "TabBar_MoveDown"))

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

        style = self.p.GetString("Style")
        if style == "Text":
            textRB.setChecked(True)
        elif style == "IconText":
            iconTextRB.setChecked(True)
        else:
            iconRB.setChecked(True)
        orientation = self.p.GetString("Orientation")
        if orientation == "North":
            topRB.setChecked(True)
        elif orientation == "South":
            bottomRB.setChecked(True)
        elif orientation == "West":
            leftRB.setChecked(True)
        elif orientation == "East":
            rightRB.setChecked(True)
        else:
            autoRB.setChecked(True)
        prefbutton = self.p.GetString("PrefButton", "On")
        if prefbutton == "On":
            onRB.setChecked(True)
        else:
            offRB.setChecked(True)

        # Set connections
        iconRB.toggled.connect(self.onStyleChanged)
        textRB.toggled.connect(self.onStyleChanged)
        iconTextRB.toggled.connect(self.onStyleChanged)
        autoRB.toggled.connect(self.onOrientChanged)
        topRB.toggled.connect(self.onOrientChanged)
        bottomRB.toggled.connect(self.onOrientChanged)
        leftRB.toggled.connect(self.onOrientChanged)
        rightRB.toggled.connect(self.onOrientChanged)
        onRB.toggled.connect(self.onPrefChanged)
        offRB.toggled.connect(self.onPrefChanged)
        upBtn.clicked.connect(self.onUpClicked)
        downBtn.clicked.connect(self.onDownClicked)
        selector.itemChanged.connect(self.onItemChanged)
        self.finished.connect(self.onFinished)
        closeBtn.clicked.connect(self.onAccepted)

        self.styleGB = styleGB
        self.orientGB = orientGB
        self.prefBtnGB = prefBtnGB
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
                self.p.SetString("Style", i.objectName())


    def onOrientChanged(self):
        """
        Set Modern Menu orientation.
        """
        orientGB = self.orientGB
        for i in orientGB.findChildren(QtWidgets.QRadioButton):
            if i.isChecked():
                self.p.SetString("Orientation", i.objectName())

    def onPrefChanged(self):
        """
        Set pref button.
        """
        prefBtnGB = self.prefBtnGB
        for i in prefBtnGB.findChildren(QtWidgets.QRadioButton):
            if i.isChecked():
                self.p.SetString("PrefButton", i.objectName())