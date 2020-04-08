
import FreeCADGui, FreeCAD
from PySide import QtGui, QtCore
import os

actions = {}
mw = FreeCADGui.getMainWindow()
group = QtGui.QActionGroup(mw)
p = FreeCAD.ParamGet("User parameter:BaseApp/ModernUI")
path = os.path.dirname(__file__) + "/Resources/icons/"

def wbIcon(i):
    """Create workbench icon."""
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

def wbActions():
    """Create workbench actions."""
    wbList = FreeCADGui.listWorkbenches()
    for i in wbList:
        if i not in actions:
            action = QtGui.QAction(group)
            action.setCheckable(True)
            action.setText(wbList[i].MenuText)
            action.setData(i)
            try:
                action.setIcon(wbIcon(wbList[i].Icon))
            except:
                action.setIcon(QtGui.QIcon(":/icons/freecad"))
            actions[i] = action

def defaults():
    """Sorted string of available workbenches."""
    d = FreeCADGui.listWorkbenches()
    d = list(d)
    d.sort()
    d = ",".join(d)
    return d

default = defaults()
enabled = p.GetString("Enabled", default)
enabled = enabled.split(",")
partially = p.GetString("Partially")
partially = partially.split(",")
unchecked = p.GetString("Unchecked")
unchecked = unchecked.split(",")
position = p.GetString("Position")
position = position.split(",")

def prefDialog():
    """Preferences dialog."""
    wbActions()
    dialog = QtGui.QDialog(mw)
    dialog.setModal(True)
    dialog.resize(800, 450)
    dialog.setWindowTitle("Modern UI Preferences")
    layout = QtGui.QVBoxLayout()
    dialog.setLayout(layout)
    selector = QtGui.QListWidget(dialog)
    selector.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    btnClose = QtGui.QPushButton("Close", dialog)
    btnClose.setToolTip("Close the preferences dialog")
    btnClose.setDefault(True)
    btnUp = QtGui.QPushButton(dialog)
    btnUp.setToolTip("Move selected item up")
    btnUp.setIcon(QtGui.QIcon(path + "TabBar_MoveUp"))
    btnDown = QtGui.QPushButton(dialog)
    btnDown.setToolTip("Move selected item down")
    btnDown.setIcon(QtGui.QIcon(path + "TabBar_MoveDown"))
    l0 = QtGui.QVBoxLayout()
    g0 = QtGui.QGroupBox("Style:")
    g0.setLayout(l0)
    r0 = QtGui.QRadioButton("Icon", g0)
    r0.setObjectName("Icon")
    r0.setToolTip("Modern Menu icon style")
    r1 = QtGui.QRadioButton("Text", g0)
    r1.setObjectName("Text")
    r1.setToolTip("Modern Menu text style")
    r2 = QtGui.QRadioButton("Icon and text", g0)
    r2.setObjectName("IconText")
    r2.setToolTip("Modern Menu icon and text style")
    l0.addWidget(r0)
    l0.addWidget(r1)
    l0.addWidget(r2)
    l1 = QtGui.QVBoxLayout()
    g1 = QtGui.QGroupBox("Tab orientation:")
    g1.setLayout(l1)
    r3 = QtGui.QRadioButton("Auto", g1)
    r3.setObjectName("Auto")
    r3.setToolTip("Set based on the orientation")
    r4 = QtGui.QRadioButton("Top", g1)
    r4.setObjectName("North")
    r4.setToolTip("Tabs at top")
    r5 = QtGui.QRadioButton("Bottom", g1)
    r5.setObjectName("South")
    r5.setToolTip("Tabs at bottom")
    r6 = QtGui.QRadioButton("Left", g1)
    r6.setObjectName("West")
    r6.setToolTip("Tabs at left")
    r7 = QtGui.QRadioButton("Right", g1)
    r7.setObjectName("East")
    r7.setToolTip("Tabs at right")
    l1.addWidget(r3)
    l1.addWidget(r4)
    l1.addWidget(r5)
    l1.addWidget(r6)
    l1.addWidget(r7)
    l2 = QtGui.QHBoxLayout()
    l2.addWidget(btnUp)
    l2.addWidget(btnDown)
    l2.addStretch(1)
    l2.addWidget(btnClose)
    l3 = QtGui.QHBoxLayout()
    l3.addStretch()
    l4 = QtGui.QVBoxLayout()
    l4.addWidget(g0)
    l4.addWidget(g1)
    l6 = QtGui.QVBoxLayout()
    g6 = QtGui.QGroupBox("Preferences button on tabbar:")
    g6.setLayout(l6)
    r8 = QtGui.QRadioButton("On", g6)
    r8.setObjectName("On")
    r8.setToolTip("A preference button appears on the right/bottom of the tabbar")
    r9 = QtGui.QRadioButton("Off", g6)
    r9.setObjectName("Off")
    r8.setToolTip("No button on the tabbar (only via menu Tools -> Acessories")
    l6.addWidget(r8)
    l6.addWidget(r9)
    l4.addWidget(g6)
    l4.addStretch()
    l4.insertLayout(0, l3)
    l5 = QtGui.QHBoxLayout()
    l5.addWidget(selector)
    l5.insertLayout(1, l4)
    layout.insertLayout(0, l5)
    layout.insertLayout(1, l2)

    def onAccepted():
        """Close dialog on button close."""
        dialog.done(1)

    def onFinished():
        """Delete dialog on close."""
        dialog.deleteLater()

    def onItemChanged(item=None):
        """Save workbench list state."""
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
        p.SetString("Enabled", ",".join(enabled))
        p.SetString("Partially", ",".join(partially))
        p.SetString("Unchecked", ",".join(unchecked))

    def onUp():
        """Save workbench position list."""
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
            p.SetString("Position", ",".join(position))
            onItemChanged()

    def onDown():
        """Save workbench position list."""
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
            p.SetString("Position", ",".join(position))
            onItemChanged()

    def onG0(r):
        """Set Modern Menu style."""
        if r:
            for i in g0.findChildren(QtGui.QRadioButton):
                if i.isChecked():
                    p.SetString("Style", i.objectName())


    def onG1(r):
        """Set Modern Menu orientation."""
        if r:
            for i in g1.findChildren(QtGui.QRadioButton):
                if i.isChecked():
                    p.SetString("Orientation", i.objectName())

    def onG6(r):
        """Set pref button."""
        if r:
            for i in g6.findChildren(QtGui.QRadioButton):
                if i.isChecked():
                    p.SetString("PrefButton", i.objectName())

    default = defaults()
    enabled = p.GetString("Enabled", default)
    enabled = enabled.split(",")
    partially = p.GetString("Partially")
    partially = partially.split(",")
    unchecked = p.GetString("Unchecked")
    unchecked = unchecked.split(",")
    position = p.GetString("Position")
    position = position.split(",")
    default = default.split(",")
    for i in default:
        if i not in position:
            position.append(i)
    for i in position:
        if i in actions:
            item = QtGui.QListWidgetItem(selector)
            item.setText(actions[i].text())
            item.setIcon(actions[i].icon())
            item.setData(32, actions[i].data())
            if actions[i].data() in enabled:
                item.setCheckState(QtCore.Qt.CheckState(2))
                item.setData(50, "Checked")
            elif actions[i].data() in partially:
                item.setCheckState(QtCore.Qt.CheckState(1))
                item.setData(50, "Partially")
            elif actions[i].data() in unchecked:
                item.setCheckState(QtCore.Qt.CheckState(0))
                item.setData(50, "Unchecked")
            else:
                item.setCheckState(QtCore.Qt.CheckState(2))
                item.setData(50, "Checked")

    style = p.GetString("Style")
    if style == "Text":
        r1.setChecked(True)
    elif style == "IconText":
        r2.setChecked(True)
    else:
        r0.setChecked(True)
    orientation = p.GetString("Orientation")
    if orientation == "North":
        r4.setChecked(True)
    elif orientation == "South":
        r5.setChecked(True)
    elif orientation == "West":
        r6.setChecked(True)
    elif orientation == "East":
        r7.setChecked(True)
    else:
        r3.setChecked(True)
    prefbutton = p.GetString("PrefButton", "On")
    if prefbutton == "On":
        r8.setChecked(True)
    else:
        r9.setChecked(True)
    r0.toggled.connect(onG0)
    r1.toggled.connect(onG0)
    r2.toggled.connect(onG0)
    r3.toggled.connect(onG1)
    r4.toggled.connect(onG1)
    r5.toggled.connect(onG1)
    r6.toggled.connect(onG1)
    r7.toggled.connect(onG1)
    r8.toggled.connect(onG6)
    r9.toggled.connect(onG6)
    btnUp.clicked.connect(onUp)
    btnDown.clicked.connect(onDown)
    selector.itemChanged.connect(onItemChanged)
    dialog.finished.connect(onFinished)
    btnClose.clicked.connect(onAccepted)

    return dialog


def showPreferences():
    """Open the preferences dialog."""
    dialog = prefDialog()
    dialog.show()